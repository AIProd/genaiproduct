import polars as pl

from modules.global_utils import ProcessorHelper
from modules.sales import constants
from modules.sales.processors.annual_processor import AnnualProcessor
from modules.sales.processors.mat_processor import MATProcessor
from modules.sales.processors.mat_processor_ungrouped import MATProcessorUngrouped
from modules.sales.processors.monthly_processor import MonthlyProcessor
from modules.sales.processors.rolq_processor import ROLQProcessor

from modules.sales.processors.annual_processor_territory import AnnualProcessorTerritory
from modules.sales.processors.mat_processor_territory import MATProcessorTerritory
from modules.sales.processors.monthly_processor_territory import MonthlyProcessorTerritory
from modules.sales.processors.rolq_processor_territory import ROLQProcessorTerritory
from modules.sales.processors.rolq_processor_ungrouped import ROLQProcessorUngrouped


class SalesDataProcessor:
    """
    Class to process sales data and calculate various sales metrics using different processors.
    """

    def __init__(self, input_lazy_frame: pl.LazyFrame):
        """
        Initialize the SalesDataProcessor with input data.

        :param input_lazy_frame: The input sales data as a Polars LazyFrame.
        :type input_lazy_frame: pl.LazyFrame
        """
        self.input_lazy_frame = input_lazy_frame
        self._processor_classes = {
            'MonthlyProcessor': MonthlyProcessor,
            'AnnualProcessor': AnnualProcessor,
            'MATProcessor': MATProcessor,
            'MATProcessorUngrouped': MATProcessorUngrouped,
            'ROLQProcessor': ROLQProcessor,
            'ROLQProcessorUngrouped': ROLQProcessorUngrouped,
            'MonthlyProcessorTerritory': MonthlyProcessorTerritory,
            'AnnualProcessorTerritory': AnnualProcessorTerritory,
            'MATProcessorTerritory': MATProcessorTerritory,
            'ROLQProcessorTerritory': ROLQProcessorTerritory

        }

    @property
    def processor_classes(self) -> dict:
        """
        Get the mapping of processor names to their classes.

        :return: A dictionary mapping processor names to processor classes.
        :rtype: dict
        """
        return self._processor_classes

    def process_processor(
            self,
            processor_name: str,
            compute: bool = True
    ) -> pl.LazyFrame | pl.DataFrame:
        """
        Process data using the specified processor.

        :param processor_name: The name of the processor to use. Must be one of the keys in `processor_classes`.
        :type processor_name: str
        :param compute: Whether to compute the result and return a DataFrame (`True`) or return a LazyFrame (`False`).
                        Default is `True`.
        :type compute: bool, optional
        :return: The processed data. Type depends on the `compute` parameter.
        :rtype: pl.DataFrame or pl.LazyFrame
        :raises ValueError: If the specified `processor_name` is not available in `processor_classes`.
        """
        if processor_name not in self.processor_classes:
            raise ValueError(f"Processor '{processor_name}' is not available.")

        processor_class = self.processor_classes[processor_name]
        processor_object = processor_class(self.input_lazy_frame)
        output_lazy_frame = processor_object.process()
        del processor_object
        output_lazy_frame = ProcessorHelper.enforce_metrics_schema(output_lazy_frame)

        return output_lazy_frame.collect() if compute else output_lazy_frame

    def process_data(self, compute: bool = True) -> pl.LazyFrame | pl.DataFrame:
        """
        Process data using all available processors and combine the output.

        :param compute: Whether to compute the result and return a DataFrame (`True`) or return a LazyFrame (`False`).
                        Default is `True`.
        :type compute: bool, optional
        :return: The combined processed data from all processors.
        :rtype: pl.DataFrame or pl.LazyFrame
        """
        combined_lazy_frame = pl.LazyFrame()

        for processor_name in self.processor_classes:
            processor_lazy_frame = self.process_processor(processor_name, compute=False)
            combined_lazy_frame = pl.concat([combined_lazy_frame, processor_lazy_frame])

        return combined_lazy_frame.collect() if compute else combined_lazy_frame
