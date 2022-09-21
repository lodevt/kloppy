import sys

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import (
    Dict,
    List,
    Type,
    Union,
    Any,
    Callable,
    Optional,
    Iterable,
    overload,
    TYPE_CHECKING,
    Generic,
    TypeVar,
)

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from kloppy.domain.models.common import DatasetType
from kloppy.utils import (
    camelcase_to_snakecase,
    removes_suffix,
    docstring_inherit_attributes,
)

from .common import DataRecord, Dataset, Player, Team
from .formation import FormationType
from .pitch import Point

from ...exceptions import OrphanedRecordError, InvalidFilterError

if TYPE_CHECKING:
    from ..services.transformers.event import Column


class ResultType(Enum):
    @property
    @abstractmethod
    def is_success(self):
        raise NotImplementedError

    def __str__(self):
        return self.value


class ShotResult(ResultType):
    """
    ShotResult

    Attributes:
        GOAL (ShotResult): Shot resulted in a goal
        OFF_TARGET (ShotResult): Shot was off target
        POST (ShotResult): Shot hit the post
        BLOCKED (ShotResult): Shot was blocked by another player
        SAVED (ShotResult): Shot was saved by the keeper
    """

    GOAL = "GOAL"
    OFF_TARGET = "OFF_TARGET"
    POST = "POST"
    BLOCKED = "BLOCKED"
    SAVED = "SAVED"
    OWN_GOAL = "OWN_GOAL"

    @property
    def is_success(self):
        """
        Returns if the shot was a goal
        """
        return self == self.GOAL


class PassResult(ResultType):
    """
    PassResult

    Attributes:
        COMPLETE (PassResult): Complete pass
        INCOMPLETE (PassResult): Incomplete pass (intercepted)
        OUT (PassResult): Ball went out
        OFFSIDE (PassResult): Offside
    """

    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    OUT = "OUT"
    OFFSIDE = "OFFSIDE"

    @property
    def is_success(self):
        """
        Returns if the pass was complete
        """
        return self == self.COMPLETE


class TakeOnResult(ResultType):
    """
    TakeOnResult

    Attributes:
        COMPLETE (TakeOnResult): Complete take-on
        INCOMPLETE (TakeOnResult): Incomplete take-on
        OUT (TakeOnResult): Ball went out
    """

    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    OUT = "OUT"

    @property
    def is_success(self):
        """
        Returns if the take-on was complete
        """
        return self == self.COMPLETE


class CarryResult(ResultType):
    """
    CarryResult

    Attributes:
        COMPLETE (CarryResult): Complete carry
        INCOMPLETE (CarryResult): Incomplete carry
    """

    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"

    @property
    def is_success(self):
        """
        Returns if the carry was complete
        """
        return self == self.COMPLETE


class CardType(Enum):
    """
    CardType

    Attributes:
        FIRST_YELLOW (CardType): First yellow card
        SECOND_YELLOW (CardType): Second yellow card
        RED (CardType): Red card
    """

    FIRST_YELLOW = "FIRST_YELLOW"
    SECOND_YELLOW = "SECOND_YELLOW"
    RED = "RED"


class EventType(Enum):
    """
    Attributes:
        GENERIC (EventType): Unrecognised event type
        PASS (EventType):
        SHOT (EventType):
        TAKE_ON (EventType):
        CARRY (EventType):
        SUBSTITUTION (EventType):
        CARD (EventType):
        PLAYER_ON (EventType):
        PLAYER_OFF (EventType):
        RECOVERY (EventType):
        BALL_OUT (EventType):
        FOUL_COMMITTED (EventType):
        FORMATION_CHANGE (EventType):
    """

    GENERIC = "generic"

    PASS = "PASS"
    SHOT = "SHOT"
    TAKE_ON = "TAKE_ON"
    CARRY = "CARRY"
    SUBSTITUTION = "SUBSTITUTION"
    CARD = "CARD"
    PLAYER_ON = "PLAYER_ON"
    PLAYER_OFF = "PLAYER_OFF"
    RECOVERY = "RECOVERY"
    BALL_OUT = "BALL_OUT"
    FOUL_COMMITTED = "FOUL_COMMITTED"
    FORMATION_CHANGE = "FORMATION_CHANGE"

    def __repr__(self):
        return self.value


@dataclass
class Qualifier(ABC):
    value: None

    @abstractmethod
    def to_dict(self):
        """
        Return the qualifier as a dict
        """
        pass

    @property
    def name(self):
        return camelcase_to_snakecase(
            removes_suffix(type(self).__name__, "Qualifier")
        )


@dataclass
class BoolQualifier(Qualifier, ABC):
    value: bool

    def to_dict(self):
        return {f"is_{self.name}": self.value}


class EnumQualifier(Qualifier, ABC):
    value: Enum

    def to_dict(self):
        return {f"{self.name}_type": self.value.value}


class SetPieceType(Enum):
    """
    SetPieceType

    Attributes:
        GOAL_KICK (SetPieceType):
        FREE_KICK (SetPieceType):
        THROW_IN (SetPieceType):
        CORNER_KICK (SetPieceType):
        PENALTY (SetPieceType):
        KICK_OFF (SetPieceType):
    """

    GOAL_KICK = "GOAL_KICK"
    FREE_KICK = "FREE_KICK"
    THROW_IN = "THROW_IN"
    CORNER_KICK = "CORNER_KICK"
    PENALTY = "PENALTY"
    KICK_OFF = "KICK_OFF"


@dataclass
class SetPieceQualifier(EnumQualifier):
    """
    SetPieceQualifier

    Attributes:
        value: Specifies the type of set piece
    """

    value: SetPieceType


@dataclass
class CardQualifier(EnumQualifier):
    """
    CardQualifier

    Attributes:
        value: Specifies the type card
    """

    value: CardType


class PassType(Enum):
    """
    PassType

    Attributes:
        CROSS (PassType):
        HAND_PASS (PassType):
        HEAD_PASS (PassType):
        HIGH_PASS (PassType):
        LAUNCH (PassType):
        SIMPLE_PASS (PassType):
        SMART_PASS (PassType):
        LONG_BALL (PassType)
        THROUGH_BALL (PassType)
        CHIPPED_PASS (PassType)
        FLICK_ON (PassType)
        ASSIST (PassType)
        ASSIST_2ND (PassType)
        SWITCH_OF_PLAY (PassType)
    """

    CROSS = "CROSS"
    HAND_PASS = "HAND_PASS"
    HEAD_PASS = "HEAD_PASS"
    HIGH_PASS = "HIGH_PASS"
    LAUNCH = "LAUNCH"
    SIMPLE_PASS = "SIMPLE_PASS"
    SMART_PASS = "SMART_PASS"
    LONG_BALL = "LONG_BALL"
    THROUGH_BALL = "THROUGH_BALL"
    CHIPPED_PASS = "CHIPPED_PASS"
    FLICK_ON = "FLICK_ON"
    ASSIST = "ASSIST"
    ASSIST_2ND = "ASSIST_2ND"
    SWITCH_OF_PLAY = "SWITCH_OF_PLAY"


@dataclass
class PassQualifier(EnumQualifier):
    value: PassType


class BodyPart(Enum):
    """
    BodyPart

    Attributes:
        RIGHT_FOOT (BodyPart): Pass or Shot with right foot, save with right foot (for goalkeepers).
        LEFT_FOOT (BodyPart): Pass or Shot with leftt foot, save with left foot (for goalkeepers).
        HEAD (BodyPart): Pass or Shot with head, save with head (for goalkeepers).
        BOTH_HANDS (BodyPart): Goalkeeper only. Save with both hands.
        CHEST (BodyPart): Goalkeeper only. Save with chest.
        LEFT_HAND (BodyPart): Goalkeeper only. Save with left hand.
        RIGHT_HAND (BodyPart): Goalkeeper only. Save with right hand.
        DROP_KICK (BodyPart): Pass is a keeper drop kick.
        KEEPER_ARM (BodyPart): Pass thrown from keepers hands.
        OTHER (BodyPart): Other body part (chest, back, etc.), for Pass and Shot.
        NO_TOUCH (BodyPart): Pass only. A player deliberately let the pass go past him
                             instead of receiving it to deliver to a teammate behind him.
                             (Also known as a "dummy").
    """

    RIGHT_FOOT = "RIGHT_FOOT"
    LEFT_FOOT = "LEFT_FOOT"
    HEAD = "HEAD"

    BOTH_HANDS = "BOTH_HANDS"
    CHEST = "CHEST"
    LEFT_HAND = "LEFT_HAND"
    RIGHT_HAND = "RIGHT_HAND"
    DROP_KICK = "DROP_KICK"
    KEEPER_ARM = "KEEPER_ARM"
    OTHER = "OTHER"
    NO_TOUCH = "NO_TOUCH"


@dataclass
class BodyPartQualifier(EnumQualifier):
    value: BodyPart


class GoalkeeperAction(Enum):
    REFLEX = "REFLEX"
    SAVE_ATTEMPT = "SAVE_ATTEMPT"


@dataclass
class GoalkeeperActionQualifier(EnumQualifier):
    value: GoalkeeperAction


@dataclass
class CounterAttackQualifier(BoolQualifier):
    pass


@dataclass
@docstring_inherit_attributes(DataRecord)
class Event(DataRecord, ABC):
    """
    Abstract event baseclass. All other event classes inherit from this class.

    Attributes:
        event_id: identifier given by provider
        team: See [`Team`][kloppy.domain.models.common.Team]
        player: See [`Player`][kloppy.domain.models.common.Player]
        coordinates: Coordinates where event happened. See [`Point`][kloppy.domain.models.pitch.Point]
        raw_event: Dict
        state: Dict[str, Any]
        qualifiers: See [`Qualifier`][kloppy.domain.models.event.Qualifier]
    """

    event_id: str
    team: Team
    player: Player
    coordinates: Point

    result: Optional[ResultType]

    raw_event: Dict
    state: Dict[str, Any]
    related_event_ids: List[str]

    qualifiers: List[Qualifier]

    @property
    def record_id(self) -> str:
        return self.event_id

    @property
    @abstractmethod
    def event_type(self) -> EventType:
        raise NotImplementedError

    @property
    @abstractmethod
    def event_name(self) -> str:
        raise NotImplementedError

    @classmethod
    def create(cls, **kwargs):
        extra_kwargs = {"state": {}}
        if "related_event_ids" not in kwargs:
            extra_kwargs["related_event_ids"] = []
        return cls(**kwargs, **extra_kwargs)

    def get_qualifier_value(self, qualifier_type: Type[Qualifier]):
        """
        Returns the Qualifier of a certain type, or None if qualifier is not present.

        Arguments:
            qualifier_type: one of the following QualifierTypes: [`SetPieceQualifier`][kloppy.domain.models.event.SetPieceQualifier]
                [`BodyPartQualifier`][kloppy.domain.models.event.BodyPartQualifier] [`PassQualifier`][kloppy.domain.models.event.PassQualifier]

        Examples:
            >>> from kloppy.domain import SetPieceQualifier
            >>> pass_event.get_qualifier_value(SetPieceQualifier)
            <SetPieceType.GOAL_KICK: 'GOAL_KICK'>
        """
        if self.qualifiers:
            for qualifier in self.qualifiers:
                if isinstance(qualifier, qualifier_type):
                    return qualifier.value
        return None

    def get_related_events(self) -> List["Event"]:
        if not self.dataset:
            raise OrphanedRecordError()

        return [
            self.dataset.get_record_by_id(event_id)
            for event_id in self.related_event_ids
        ]

    def get_related_event(
        self, type_: Union[str, EventType]
    ) -> Optional["Event"]:
        event_type = (
            EventType[type_.upper()] if isinstance(type_, str) else type_
        )
        for related_event in self.get_related_events():
            if related_event.event_type == event_type:
                return related_event
        return None

    """Define all related events for easy access"""

    def related_pass(self) -> Optional["PassEvent"]:
        return self.get_related_event(EventType.PASS)

    def related_shot(self) -> Optional["ShotEvent"]:
        return self.get_related_event(EventType.SHOT)

    def related_take_on(self) -> Optional["TakeOnEvent"]:
        return self.get_related_event(EventType.TAKE_ON)

    def related_carry(self) -> Optional["CarryEvent"]:
        return self.get_related_event(EventType.CARRY)

    def related_substitution(self) -> Optional["SubstitutionEvent"]:
        return self.get_related_event(EventType.SUBSTITUTION)

    def related_card(self) -> Optional["CardEvent"]:
        return self.get_related_event(EventType.CARD)

    def related_player_on(self) -> Optional["PlayerOnEvent"]:
        return self.get_related_event(EventType.PLAYER_ON)

    def related_player_off(self) -> Optional["PlayerOffEvent"]:
        return self.get_related_event(EventType.PLAYER_OFF)

    def related_recovery(self) -> Optional["RecoveryEvent"]:
        return self.get_related_event(EventType.RECOVERY)

    def related_ball_out(self) -> Optional["BallOutEvent"]:
        return self.get_related_event(EventType.BALL_OUT)

    def related_foul_committed(self) -> Optional["FoulCommittedEvent"]:
        return self.get_related_event(EventType.FOUL_COMMITTED)

    def related_formation_change(self) -> Optional["FormationChangeEvent"]:
        return self.get_related_event(EventType.FORMATION_CHANGE)

    def matches(self, filter_) -> bool:
        if filter_ is None:
            return True
        elif callable(filter_):
            return filter_(self)
        elif isinstance(filter_, str):
            """
            Allowed formats:
            1. <event_type>
            2. <event_type>.<result>

            This format always us to go to css selectors without breaking existing code.
            """
            parts = filter_.upper().split(".")
            if len(parts) == 2:
                event_type, result = parts
            elif len(parts) == 1:
                event_type = parts[0]
                result = None
            else:
                raise InvalidFilterError(
                    f"Don't know how to apply filter {filter_}"
                )

            if event_type:
                try:
                    if self.event_type != EventType[event_type]:
                        return False
                except KeyError:
                    raise InvalidFilterError(
                        f"Cannot find event type {event_type}. Possible options: {[e.value.lower() for e in EventType]}"
                    )

            if result:
                if not self.result:
                    return False

                try:
                    if self.result != self.result.__class__[result]:
                        return False
                except KeyError:
                    # result isn't applicable for this event
                    # example: result='GOAL' event=<Pass>
                    return False

            return True

    def __str__(self):
        m, s = divmod(self.timestamp, 60)

        event_type = (
            self.__class__.__name__
            if not isinstance(self, GenericEvent)
            else f"GenericEvent:{self.event_name}"
        )

        return (
            f"<{event_type} "
            f"event_id='{self.event_id}' "
            f"time='P{self.period.id}T{m:02.0f}:{s:02.0f}' "
            f"player='{self.player}' "
            f"result='{self.result}'>"
        )

    def __repr__(self):
        return str(self)


@dataclass(repr=False)
@docstring_inherit_attributes(Event)
class GenericEvent(Event):
    """
    GenericEvent

    Attributes:
        event_type (EventType): `EventType.GENERIC` (See [`EventType`][kloppy.domain.models.event.EventType])
        event_name (str): `"generic"`
    """

    event_type: EventType = EventType.GENERIC
    event_name: str = "generic"


@dataclass(repr=False)
@docstring_inherit_attributes(Event)
class ShotEvent(Event):
    """
    ShotEvent

    Attributes:
        event_type (EventType): `EventType.SHOT` (See [`EventType`][kloppy.domain.models.event.EventType])
        event_name (str): `"shot"`,
        result_coordinates (Point): See [`Point`][kloppy.domain.models.pitch.Point]
        result (ShotResult): See [`ShotResult`][kloppy.domain.models.event.ShotResult]
    """

    result: ShotResult
    result_coordinates: Point = None

    event_type: EventType = EventType.SHOT
    event_name: str = "shot"


@dataclass(repr=False)
@docstring_inherit_attributes(Event)
class PassEvent(Event):
    """
    PassEvent

    Attributes:
        event_type (EventType): `EventType.PASS` (See [`EventType`][kloppy.domain.models.event.EventType])
        event_name (str): `"pass"`
        receive_timestamp (float):
        receiver_coordinates (Point): See [`Point`][kloppy.domain.models.pitch.Point]
        receiver_player (Player): See [`Player`][kloppy.domain.models.common.Player]
        result (PassResult): See [`PassResult`][kloppy.domain.models.event.PassResult]
    """

    receive_timestamp: float
    receiver_player: Player
    receiver_coordinates: Point

    result: PassResult

    event_type: EventType = EventType.PASS
    event_name: str = "pass"


@dataclass(repr=False)
@docstring_inherit_attributes(Event)
class TakeOnEvent(Event):
    """
    TakeOnEvent

    Attributes:
        event_type (EventType): `EventType.TAKE_ON` (See [`EventType`][kloppy.domain.models.event.EventType])
        event_name (str): `"take_on"`,
        result (TakeOnResult): See [`TakeOnResult`][kloppy.domain.models.event.TakeOnResult]
    """

    result: TakeOnResult

    event_type: EventType = EventType.TAKE_ON
    event_name: str = "take_on"


@dataclass(repr=False)
@docstring_inherit_attributes(Event)
class CarryEvent(Event):
    """
    CarryEvent

    Attributes:
        event_type (EventType): `EventType.CARRY` (See [`EventType`][kloppy.domain.models.event.EventType])
        event_name (str): `"carry"`,
        end_timestamp (float):
        end_coordinates (Point): See [`Point`][kloppy.domain.models.pitch.Point]
        result (CarryResult): See [`CarryResult`][kloppy.domain.models.event.CarryResult]
    """

    end_timestamp: float
    end_coordinates: Point

    result: CarryResult

    event_type: EventType = EventType.CARRY
    event_name: str = "carry"


@dataclass(repr=False)
@docstring_inherit_attributes(Event)
class SubstitutionEvent(Event):
    """
    SubstitutionEvent

    Attributes:
        event_type (EventType): `EventType.SUBSTITUTION` (See [`EventType`][kloppy.domain.models.event.EventType])
        event_name (str): `"substitution"`,
        replacement_player (Player): See [`Player`][kloppy.domain.models.common.Player]
    """

    replacement_player: Player

    event_type: EventType = EventType.SUBSTITUTION
    event_name: str = "substitution"


@dataclass(repr=False)
@docstring_inherit_attributes(Event)
class PlayerOffEvent(Event):
    """
    PlayerOffEvent

    Attributes:
        event_type (EventType): `EventType.PLAYER_OFF` (See [`EventType`][kloppy.domain.models.event.EventType])
        event_name (str): `"player_off"`
    """

    event_type: EventType = EventType.PLAYER_OFF
    event_name: str = "player_off"


@dataclass(repr=False)
@docstring_inherit_attributes(Event)
class PlayerOnEvent(Event):
    """
    PlayerOnEvent

    Attributes:
        event_type (EventType): `EventType.PLAYER_ON` (See [`EventType`][kloppy.domain.models.event.EventType])
        event_name (str): `"player_on"`
    """

    event_type: EventType = EventType.PLAYER_ON
    event_name: str = "player_on"


@dataclass(repr=False)
@docstring_inherit_attributes(Event)
class CardEvent(Event):
    """
    CardEvent

    Attributes:
        event_type (EventType): `EventType.CARD` (See [`EventType`][kloppy.domain.models.event.EventType])
        event_name (str): `"card"`
        card_type: See [`CardType`][kloppy.domain.models.event.CardType]
    """

    card_type: CardType

    event_type: EventType = EventType.CARD
    event_name: str = "card"


@dataclass(repr=False)
@docstring_inherit_attributes(Event)
class FormationChangeEvent(Event):
    """
    FormationChangeEvent

    Attributes:
        event_type (EventType): `EventType.FORMATION_CHANGE` (See [`EventType`][kloppy.domain.models.event.EventType])
        event_name (str): `"card"`
        formation_type: See [`FormationType`][kloppy.domain.models.formation.FormationType]
    """

    formation_type: FormationType

    event_type: EventType = EventType.FORMATION_CHANGE
    event_name: str = "formation_change"


@dataclass(repr=False)
@docstring_inherit_attributes(Event)
class RecoveryEvent(Event):
    """
    RecoveryEvent

    Attributes:
        event_type (EventType): `EventType.RECOVERY` (See [`EventType`][kloppy.domain.models.event.EventType])
        event_name (str): "recovery"
    """

    event_type: EventType = EventType.RECOVERY
    event_name: str = "recovery"


@dataclass(repr=False)
@docstring_inherit_attributes(Event)
class BallOutEvent(Event):
    """
    BallOutEvent

    Attributes:
        event_type (EventType): `EventType.BALL_OUT` (See [`EventType`][kloppy.domain.models.event.EventType])
        event_name (str): "ball_out"
    """

    event_type: EventType = EventType.BALL_OUT
    event_name: str = "ball_out"


@dataclass(repr=False)
@docstring_inherit_attributes(Event)
class FoulCommittedEvent(Event):
    """
    FoulCommittedEvent

    Attributes:
        event_type (EventType): `EventType.FOUL_COMMITTED` (See [`EventType`][kloppy.domain.models.event.EventType])
        event_name (str): "foul_committed"
    """

    event_type: EventType = EventType.FOUL_COMMITTED
    event_name: str = "foul_committed"


class EventFactory:
    def build_pass(self, **kwargs) -> PassEvent:
        return PassEvent.create(**kwargs)

    def build_shot(self, **kwargs) -> ShotEvent:
        return ShotEvent.create(**kwargs)

    def build_generic(self, **kwargs) -> GenericEvent:
        return GenericEvent.create(**kwargs)

    def build_recovery(self, **kwargs) -> RecoveryEvent:
        return RecoveryEvent.create(**kwargs)

    def build_take_on(self, **kwargs) -> TakeOnEvent:
        return TakeOnEvent.create(**kwargs)

    def build_carry(self, **kwargs) -> CarryEvent:
        return CarryEvent.create(**kwargs)

    def build_formation_change(self, **kwargs) -> FormationChangeEvent:
        return FormationChangeEvent.create(**kwargs)

    def build_ball_out(self, **kwargs) -> BallOutEvent:
        return BallOutEvent.create(**kwargs)

    def build_player_on(self, **kwargs) -> PlayerOnEvent:
        return PlayerOnEvent.create(**kwargs)

    def build_player_off(self, **kwargs) -> PlayerOffEvent:
        return PlayerOffEvent.create(**kwargs)

    def build_card(self, **kwargs) -> CardEvent:
        return CardEvent.create(**kwargs)

    def build_foul_committed(self, **kwargs) -> FoulCommittedEvent:
        return FoulCommittedEvent.create(**kwargs)

    def build_substitution(self, **kwargs) -> SubstitutionEvent:
        return SubstitutionEvent.create(**kwargs)


@dataclass(repr=False)
class EventDataset(Dataset[Event]):
    """
    EventDataset

    Attributes:
        metadata: See [`Metadata`][kloppy.domain.models.common.Metadata]
        records (List[Event]): See [`Event`][kloppy.domain.models.event.Event]
        dataset_type: `DatasetType.EVENT` (See [`DatasetType`][kloppy.domain.models.common.DatasetType])
        events: alias for `records`
    """

    records: List[Event]

    dataset_type: DatasetType = DatasetType.EVENT

    @property
    def events(self):
        return self.records

    def get_event_by_id(self, event_id: str) -> Event:
        return self.get_record_by_id(event_id)

    def add_state(self, *builder_keys):
        """
        See [add_state][kloppy.domain.services.state_builder.add_state]
        """
        from kloppy.domain.services.state_builder import add_state

        return add_state(self, *builder_keys)

    def to_pandas(
        self,
        record_converter: Callable[[Event], Dict] = None,
        additional_columns: Dict[
            str, Union[Callable[[Event], Any], Any]
        ] = None,
    ) -> "DataFrame":
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "Seems like you don't have pandas installed. Please"
                " install it using: pip install pandas"
            )

        if not record_converter:
            from ..services.transformers.attribute import DefaultTransformer

            record_converter = DefaultTransformer()

        def generic_record_converter(event: Event):
            row = record_converter(event)
            if additional_columns:
                for k, v in additional_columns.items():
                    if callable(v):
                        value = v(event)
                    else:
                        value = v
                    row.update({k: value})
            return row

        return pd.DataFrame.from_records(
            map(generic_record_converter, self.records)
        )

    @overload
    def to_records(
        self,
        *columns: "Column",
        as_list: Literal[True] = True,
        **named_columns: "Column",
    ) -> List[Dict[str, Any]]:
        ...

    @overload
    def to_records(
        self,
        *columns: "Column",
        as_list: Literal[False] = False,
        **named_columns: "Column",
    ) -> Iterable[Dict[str, Any]]:
        ...

    def to_records(
        self,
        *columns: "Column",
        as_list: bool = True,
        **named_columns: "Column",
    ) -> Union[List[Dict[str, Any]], Iterable[Dict[str, Any]]]:
        from ..services.transformers.event import EventToRecordTransformer

        transformer = EventToRecordTransformer(*columns, **named_columns)
        iterator = map(transformer, self.events)
        if as_list:
            return list(iterator)
        else:
            return iterator

    def to_df(self, *columns: "Column", **named_columns: "Column"):
        from pandas import DataFrame

        return DataFrame.from_records(
            self.to_records(*columns, **named_columns, as_list=False)
        )


__all__ = [
    "EnumQualifier",
    "ResultType",
    "EventType",
    "ShotResult",
    "PassResult",
    "TakeOnResult",
    "CarryResult",
    "Event",
    "GenericEvent",
    "ShotEvent",
    "PassEvent",
    "TakeOnEvent",
    "CarryEvent",
    "SubstitutionEvent",
    "PlayerOnEvent",
    "PlayerOffEvent",
    "CardEvent",
    "CardType",
    "CardQualifier",
    "FormationType",
    "FormationChangeEvent",
    "EventDataset",
    "RecoveryEvent",
    "FoulCommittedEvent",
    "BallOutEvent",
    "SetPieceType",
    "Qualifier",
    "SetPieceQualifier",
    "PassQualifier",
    "PassType",
    "BodyPart",
    "BodyPartQualifier",
    "GoalkeeperAction",
    "GoalkeeperActionQualifier",
    "CounterAttackQualifier",
    "EventFactory",
]
