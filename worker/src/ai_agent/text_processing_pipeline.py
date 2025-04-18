import io
import logging
import os
from typing import List, Optional
from datetime import date

import pandas as pd

from configs.config import settings
from .analysis_pipeline import AnalysisPipeline
from .models.data_model import AgriculturalOperation

logger = logging.getLogger(__name__)

DEFAULT_EXCEL_PATH = (
    "operations_log.xlsx"  # Default name in the current working directory
)


def process_text_message(
    text: str, message_date: date, excel_path: str = DEFAULT_EXCEL_PATH
) -> Optional[bytes]:
    """
    Processes an input text message, analyzes it to extract agricultural operations,
    logs the results to an Excel file (creating or appending), and returns the
    updated Excel file as bytes.

    Args:
        text: The raw text message to analyze.
        excel_path: The path to the Excel file for logging results.
        message_date

    Returns:
        Bytes of the updated Excel file, or None if analysis fails or produces no data
        and the file doesn't exist.
    """
    logger.info(f"Starting text processing for excel log: {excel_path}")

    try:
        pipeline = AnalysisPipeline()
    except ValueError as e:
        logger.error(f"Failed to initialize AnalysisPipeline: {e}")
        return None

    try:
        operations: List[AgriculturalOperation] = pipeline.analyze_text(
            text, message_date=message_date
        )
        if not operations:
            logger.warning(
                f"Analysis of text did not yield any operations. Text: '{text[:100]}...'"
            )

    except Exception as e:
        logger.exception(f"Error during text analysis: {e}")
        return None  # Cannot proceed if analysis fails

    new_data_df = pd.DataFrame()
    if operations:
        operations_dict_list = [op.model_dump(mode="json") for op in operations]
        try:
            new_data_df = pd.DataFrame(operations_dict_list)
            cols = list(AgriculturalOperation.model_fields.keys())
            new_data_df = new_data_df[cols]  # Reorder/select columns
        except Exception as e:
            logger.exception(f"Error creating DataFrame from analysis results: {e}")

    existing_df = pd.DataFrame()
    try:
        if os.path.exists(excel_path):
            logger.info(f"Excel log file found at {excel_path}. Reading existing data.")
            try:
                existing_df = pd.read_excel(excel_path)
                if not all(
                    col in existing_df.columns
                    for col in new_data_df.columns
                    if not new_data_df.empty
                ):
                    logger.warning(
                        f"Columns in existing Excel file {excel_path} might not fully match new data. Appending anyway."
                    )
            except Exception as e:
                logger.error(
                    f"Error reading existing Excel file {excel_path}: {e}. Proceeding as if it's empty/invalid."
                )
                existing_df = pd.DataFrame()  # Reset if read fails
        else:
            logger.info(
                f"Excel log file not found at {excel_path}. Will create a new one."
            )

        if not new_data_df.empty:
            final_df = pd.concat([existing_df, new_data_df], ignore_index=True)
            logger.info(f"Appended {len(new_data_df)} new rows to the data.")
        else:
            final_df = existing_df
            logger.info(
                "No new operations were parsed, using existing Excel data (if any)."
            )

        if final_df.empty and not os.path.exists(excel_path):
            logger.warning(
                "No existing data and no new data parsed. No Excel file will be created/returned."
            )
            return None

        final_df.to_excel(excel_path, index=False, engine="openpyxl")

        excel_buffer = io.BytesIO()
        final_df.to_excel(excel_buffer, index=False, engine="openpyxl")
        excel_buffer.seek(0)  # Rewind buffer to the beginning

        logger.info(
            f"Successfully prepared updated Excel data in memory ({len(final_df)} total rows)."
        )
        return excel_buffer.getvalue()

    except Exception as e:
        logger.exception(f"Error during Excel file processing: {e}")
        return None
