import pandas as pd

from modules.interactions.processors.email_interaction_processor import EmailInteractionProcessor
from modules.interactions.processors.mat_processor import MATProcessor
from modules.interactions.processors.monthly_processor import MonthlyProcessor
from modules.interactions.processors.next_calls import NextCallsProcessor
from modules.interactions.processors.percentage_processor import PercentageProcessor
from modules.interactions.processors.rolq_processor import ROLQProcessor


class InteractionDataProcessor:
    """
    Class to process interaction data and calculate various interaction metrics.
    """

    def __init__(self, input_data_frame: pd.DataFrame):
        """
        Initialize with input data frame.

        Parameters:
        input_data_frame (pd.DataFrame): The input interaction data.
        """
        self.input_data_frame = input_data_frame

        self.processors = [
            MonthlyProcessor.__name__,
            NextCallsProcessor.__name__,
            MATProcessor.__name__,
            ROLQProcessor.__name__,
            PercentageProcessor.__name__,
            EmailInteractionProcessor.__name__,
        ]

        self.output_data_frame = pd.DataFrame()

    def calculate_interaction_metrics(self):
        """
        Calculate interaction metrics.
        """
        for processor in self.processors:
            processor_object = globals()[processor](self.input_data_frame)
            self.output_data_frame = pd.concat([self.output_data_frame, processor_object.process()], ignore_index=True)
            del processor_object

    def get_processed_data(self) -> pd.DataFrame:
        """
        Get the processed data with calculated interaction metrics.

        Returns:
        pd.DataFrame: The processed data frame.
        """
        # Drop year and month from the final output
        self.output_data_frame = self.output_data_frame.drop(columns=['year', 'month'])
        return self.output_data_frame
