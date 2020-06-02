import logging
import sys

from kloppy import datasets, transform, to_pandas, load_statsbomb_event_data
from kloppy.infra.utils import performance_logging


def main():
    """
        This example shows the use of Statsbomb datasets, and how we can pass argument
        to the dataset loader.
    """
    logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    logger = logging.getLogger(__name__)

    dataset = datasets.load("statsbomb", {
        #"event_types": ["pass", "take_on", "carry", "shot"]
    })#, match_id=15946)

    with performance_logging("transform", logger=logger):
        # convert to TRACAB coordinates
        dataset = transform(
            dataset,
            to_orientation="FIXED_HOME_AWAY",
            to_pitch_dimensions=[(-5500, 5500), (-3300, 3300)]
        )

    with performance_logging("to pandas", logger=logger):
        dataframe = to_pandas(dataset)

    print(dataframe[:100].to_string())

    # or load it using the helper from disk
    dataset = load_statsbomb_event_data(
        "events/15946.json",
        "lineups/15946.json"
    )


if __name__ == "__main__":
    main()