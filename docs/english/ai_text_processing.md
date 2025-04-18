# AI Text Processing

This document describes the AI-based text processing functionality used to extract structured agricultural data from free-text messages.

## Overview

The system uses Mistral AI, a large language model (LLM), to analyze agricultural reports in free-text format and extract structured data about agricultural operations.

## Components

### Text Processing Pipeline

The text processing pipeline (`text_processing_pipeline.py`) is the main entry point for processing messages. It:

1. Takes a text message as input
2. Passes it to the Analysis Pipeline for processing
3. Converts the results to a DataFrame
4. Appends the new data to an existing Excel file or creates a new one
5. Returns the updated Excel file as bytes

### Analysis Pipeline

The Analysis Pipeline (`analysis_pipeline.py`) handles the core AI analysis:

1. Constructs a detailed prompt for the Mistral AI model
2. Sends the prompt to the Mistral AI API
3. Parses and validates the returned JSON data
4. Converts the results into `AgriculturalOperation` objects

### Mistral AI Client

The Mistral AI Client (`mistral_client.py`) manages communication with the Mistral AI API:

1. Sends prompts to the Mistral API
2. Handles API rate limiting
3. Processes the model's response
4. Implements error handling and retries

## Prompt Construction

The prompts sent to Mistral AI are carefully constructed to extract specific agricultural information:

1. **Task Definition**: Clear instructions on extracting agricultural operations
2. **Rules and Guidelines**: Detailed rules for parsing different data types
3. **JSON Schema**: The expected output format
4. **Reference Lists**: Known subdivisions, operations, and crops
5. **Examples**: Sample inputs and outputs to guide the model

## Data Extraction

The system extracts the following information from agricultural reports:

- **Date**: When the operation was performed
- **Subdivision**: The farm subdivision where the operation took place
- **Operation**: The type of agricultural operation
- **Crop**: The crop being processed
- **Daily Area**: Area processed on the reported day
- **Total Area**: Cumulative area processed
- **Daily Yield**: Yield collected on the reported day
- **Total Yield**: Cumulative yield collected

## Rate Limiting

To prevent API overuse, the system implements a rate limiter (`utils/rate_limiter.py`) that:

1. Tracks API call frequency
2. Enforces a maximum number of calls per minute
3. Delays execution if the rate limit is reached

## Example Processing

```
Input:
"""
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

Output:
[
  {
    "date": "2025-03-30",
    "subdivision": "СП Коломейцево",
    "operation": "Предпосевная культивация",
    "crop": "Подсолнечник товарный",
    "daily_area": 30.0,
    "total_area": 187.0,
    "daily_yield": null,
    "total_yield": null
  },
  {
    "date": "2025-03-30",
    "subdivision": "СП Коломейцево",
    "operation": "Сев",
    "crop": "Подсолнечник товарный",
    "daily_area": 57.0,
    "total_area": 157.0,
    "daily_yield": null,
    "total_yield": null
  }
] 