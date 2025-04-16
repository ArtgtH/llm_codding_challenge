import io
import logging
import os
from typing import List, Optional

import pandas as pd
from pydantic import ValidationError

from .analysis_pipeline import AnalysisPipeline
from .models.data_model import AgriculturalOperation

logger = logging.getLogger(__name__)

DEFAULT_EXCEL_PATH = "operations_log.xlsx" # Default name in the current working directory

def process_text_message(text: str, excel_path: str = DEFAULT_EXCEL_PATH) -> Optional[bytes]:
    """
    Processes an input text message, analyzes it to extract agricultural operations,
    logs the results to an Excel file (creating or appending), and returns the 
    updated Excel file as bytes.

    Args:
        text: The raw text message to analyze.
        excel_path: The path to the Excel file for logging results.

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
        operations: List[AgriculturalOperation] = pipeline.analyze_text(text)
        if not operations:
            logger.warning(f"Analysis of text did not yield any operations. Text: '{text[:100]}...'")

    except Exception as e:
        logger.exception(f"Error during text analysis: {e}")
        return None # Cannot proceed if analysis fails

    new_data_df = pd.DataFrame()
    if operations:
        operations_dict_list = [op.model_dump(mode='json') for op in operations]
        try:
            new_data_df = pd.DataFrame(operations_dict_list)
            cols = list(AgriculturalOperation.model_fields.keys())
            new_data_df = new_data_df[cols] # Reorder/select columns
        except Exception as e:
             logger.exception(f"Error creating DataFrame from analysis results: {e}")

    existing_df = pd.DataFrame()
    try:
        if os.path.exists(excel_path):
            logger.info(f"Excel log file found at {excel_path}. Reading existing data.")
            try:
                existing_df = pd.read_excel(excel_path)
                 # Basic check for compatibility (e.g., check if columns roughly match)
                if not all(col in existing_df.columns for col in new_data_df.columns if not new_data_df.empty):
                     logger.warning(f"Columns in existing Excel file {excel_path} might not fully match new data. Appending anyway.")
            except Exception as e:
                logger.error(f"Error reading existing Excel file {excel_path}: {e}. Proceeding as if it's empty/invalid.")
                existing_df = pd.DataFrame() # Reset if read fails
        else:
             logger.info(f"Excel log file not found at {excel_path}. Will create a new one.")

        if not new_data_df.empty:
            # Append new data if any was parsed
            final_df = pd.concat([existing_df, new_data_df], ignore_index=True)
            logger.info(f"Appended {len(new_data_df)} new rows to the data.")
        else:
            # If no new data, just use the existing data
            final_df = existing_df
            logger.info("No new operations were parsed, using existing Excel data (if any).")

        if final_df.empty and not os.path.exists(excel_path):
            logger.warning("No existing data and no new data parsed. No Excel file will be created/returned.")
            return None

        excel_buffer = io.BytesIO()
        final_df.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_buffer.seek(0) # Rewind buffer to the beginning
        
        logger.info(f"Successfully prepared updated Excel data in memory ({len(final_df)} total rows).")
        return excel_buffer.getvalue()

    except Exception as e:
        logger.exception(f"Error during Excel file processing: {e}")
        return None

# --- Example Usage (for testing) ---
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Ensure MISTRAL_API_KEY is set as an environment variable
    if not os.getenv("MISTRAL_API_KEY"):
        print("Error: MISTRAL_API_KEY environment variable is not set for testing.")
        exit(1)

    # Example text (replace with actual test cases)
    test_message = """
    30.03.25г.
    СП Коломейцево

    предпосевная культивация  
      -под подсолнечник
        день 30га
        от начала 187га(91%)

    сев подсолнечника 
      день+ночь 57га
      от начала 157га(77%)
    """
    
    test_excel_file = "test_operations_log.xlsx" # Use a test file name

    # --- Clean up previous test file if it exists --- 
    if os.path.exists(test_excel_file):
        try:
            os.remove(test_excel_file)
            logger.info(f"Removed previous test file: {test_excel_file}")
        except OSError as e:
            logger.error(f"Error removing existing test file {test_excel_file}: {e}")

    # --- First Run (Create File) --- 
    print(f"\n--- Running first analysis for: '{test_message[:50]}...' --- ")
    excel_bytes_1 = process_text_message(test_message, excel_path=test_excel_file)

    if excel_bytes_1:
        print(f"First run successful. Received {len(excel_bytes_1)} bytes of Excel data.")
        # Save the result to check
        try:
            with open(test_excel_file, 'wb') as f:
                f.write(excel_bytes_1)
            print(f"Saved results to {test_excel_file}")
        except IOError as e:
            print(f"Error saving test file {test_excel_file}: {e}")
    else:
        print("First run failed or produced no data.")

    # --- Second Run (Append to File) --- 
    print(f"\n--- Running second analysis (should append) --- ")
    # Modify text slightly for potentially different results or just re-process
    test_message_2 = "Уборка свеклы 27.10.день \n По ПУ 45/1569 \n Вал 1259680/6660630"
    excel_bytes_2 = process_text_message(test_message_2, excel_path=test_excel_file)

    if excel_bytes_2:
        print(f"Second run successful. Received {len(excel_bytes_2)} bytes of Excel data.")
        # Save the result again to check the appended data
        try:
            with open(test_excel_file, 'wb') as f:
                f.write(excel_bytes_2)
            print(f"Saved updated results to {test_excel_file}")
        except IOError as e:
            print(f"Error saving updated test file {test_excel_file}: {e}")
            
        # Optional: Read back and check row count
        try:
            df_check = pd.read_excel(test_excel_file)
            print(f"Checked file {test_excel_file}, found {len(df_check)} rows.")
        except Exception as e:
             print(f"Could not read back test file {test_excel_file} for checking: {e}")

    else:
        print("Second run failed or produced no data.") 