import pandas as pd

from modules.sales.processors.annual_processor import AnnualProcessor
from modules.sales.processors.mat_processor import MATProcessor
from modules.sales.processors.monthly_processor import MonthlyProcessor
from modules.sales.processors.rolq_processor import ROLQProcessor


class SalesDataProcessor:
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
            AnnualProcessor.__name__,
            MATProcessor.__name__,
            ROLQProcessor.__name__,
        ]

        self.output_data_frame = pd.DataFrame()

    def process_data(self):
        """
        Calculate sales metrics.
        """
        for processor in self.processors:
            processor_object = globals()[processor](self.input_data_frame)
            self.output_data_frame = pd.concat([self.output_data_frame, processor_object.process()], ignore_index=True)
            del processor_object

        self.output_data_frame['timestamp'] = self.output_data_frame['timestamp'].apply(lambda x: x.isoformat())

    def get_processed_data(self) -> pd.DataFrame:
        """
        Get the processed data with calculated sales metrics.

        Returns:
        pd.DataFrame: The processed data frame.
        """
        self.output_data_frame = self.output_data_frame.drop(columns=['year', 'month'])

        return self.output_data_frame
