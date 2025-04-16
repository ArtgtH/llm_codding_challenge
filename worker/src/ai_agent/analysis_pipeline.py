import json
import logging
import os
from typing import List, Optional
from datetime import date

from pydantic import ValidationError

from .mistral_client import MistralAnalysisClient
from .models.data_model import AgriculturalOperation
from .utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

# Configuration (consider moving to a config file/env vars)
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
EXTRA_DATA_PATH = os.path.join(os.path.dirname(__file__), "extra_data", "processed_data.json")

# --- Helper Functions ---

def load_extra_data(path: str) -> Optional[dict]:
    """Loads structured data from the JSON file."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Extra data file not found at {path}")
        return None
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from {path}")
        return None

def construct_prompt(text: str, schema: str, extra_data: Optional[dict]) -> str:
    """Constructs the prompt for the Mistral API, including rules, lists, and few-shot examples."""
    
    # --- Extract Reference Lists from Extra Data ---
    known_operations_list = []
    known_crops_list = []
    known_subdivisions_list = []
    
    if extra_data:
        try:
            # Extract Operation Names (filtering header/notes)
            ops_data = extra_data.get("Названия операций", {}).get("data", [])
            if ops_data:
                 known_operations_list = [item.get("Названия операций") for item in ops_data 
                                          if item.get("Названия операций") and item.get("Названия операций") != "Наименования полевых работ"]
        except Exception as e:
            logger.warning(f"Error processing known operations list: {e}")

        try:
            # Extract Crop Names (filtering header/notes)
            crops_data = extra_data.get("Наименование культур", {}).get("data", [])
            if crops_data:
                 known_crops_list = [item.get("Наименование культур") for item in crops_data 
                                     if item.get("Наименование культур") and item.get("Наименование культур") != "Наименования с/х культур"]
        except Exception as e:
            logger.warning(f"Error processing known crops list: {e}")

        try:
            # Extract Subdivision Names (filtering header/notes)
            subs_data = extra_data.get("Принадлежность отделений и ПУ", {}).get("data", [])
            if subs_data:
                 # Corrected list comprehension and set conversion for subdivisions
                 sub_names = []
                 for item in subs_data:
                     name = item.get("Принадлежность отделений и производственных участков (ПУ) к подразделениям")
                     if name and name != "Подразделение":
                         sub_names.append(name)
                 known_subdivisions_list = list(set(sub_names)) # Convert to set then back to list to get unique names
        except Exception as e:
            logger.warning(f"Error processing known subdivisions list: {e}")

    # --- Few-Shot Examples (Keep as they are valuable) ---
    few_shot_examples = """
Examples:

Input Text:
'''
Пахота зяби под сою 
По ПУ 7/1402
Отд 17 7/141

Вырав-ие зяби под кук/силос
По ПУ 16/16
Отд 12 16/16

Вырав-ие зяби под сах/свёклу
По ПУ 67/912
Отд 12 67/376

2-ое диск-ие сах/свёкла 
По ПУ 59/1041
Отд 17 59/349
'''
Expected JSON Output:
```json
[
  {"date": null, "subdivision": "АОР", "operation": "Пахота", "crop": "Соя товарная", "daily_area": 7.0, "total_area": 1402.0, "daily_yield": null, "total_yield": null},
  {"date": null, "subdivision": "АОР", "operation": "Выравнивание зяби", "crop": "Кукуруза кормовая", "daily_area": 16.0, "total_area": 16.0, "daily_yield": null, "total_yield": null},
  {"date": null, "subdivision": "АОР", "operation": "Выравнивание зяби", "crop": "Свекла сахарная", "daily_area": 67.0, "total_area": 912.0, "daily_yield": null, "total_yield": null},
  {"date": null, "subdivision": "АОР", "operation": "Дискование 2-е", "crop": "Свекла сахарная", "daily_area": 59.0, "total_area": 1041.0, "daily_yield": null, "total_yield": null}
]
```

Input Text:
'''
Уборка свеклы 27.10.день
Отд10-45/216
По ПУ 45/1569
Вал 1259680/6660630
Урожайность 279,9/308,3
По ПУ 1259680/41630600
На завод 1811630/6430580
По ПУ 1811630/41400550
Положено в кагат 399400
Вввезено с кагата 951340
Остаток 230060
Оз-9,04/12,58
Дигестия-14,50/15,05
'''
Expected JSON Output:
```json
[
  {"date": "2024-10-27", "subdivision": "АОР", "operation": "Уборка", "crop": "Свекла сахарная", "daily_area": 45.0, "total_area": 1569.0, "daily_yield": 12596.80, "total_yield": 66606.30}
]
```
(Note: Assuming current year 2024 for date '27.10'. Yield values 'Вал за день, ц' and 'Вал с начала, ц' might need division by 100 if input is in kg instead of centners (ц), clarify if needed.)


Input Text:
'''
30.03.25г.
СП Коломейцево

предпосевная культивация  
  -под подсолнечник
    день 30га
    от начала 187га(91%)

сев подсолнечника 
  день+ночь 57га
  от начала 157га(77%)

Внесение почвенного гербицида по подсолнечнику 
  день 82га 
  от начала 82га (38%)
'''
Expected JSON Output:
```json
[
  {"date": "2025-03-30", "subdivision": "СП Коломейцево", "operation": "Предпосевная культивация", "crop": "Подсолнечник товарный", "daily_area": 30.0, "total_area": 187.0, "daily_yield": null, "total_yield": null},
  {"date": "2025-03-30", "subdivision": "СП Коломейцево", "operation": "Сев", "crop": "Подсолнечник товарный", "daily_area": 57.0, "total_area": 157.0, "daily_yield": null, "total_yield": null},
  {"date": "2025-03-30", "subdivision": "СП Коломейцево", "operation": "Гербицидная обработка", "crop": "Подсолнечник товарный", "daily_area": 82.0, "total_area": 82.0, "daily_yield": null, "total_yield": null}
]
```
"""

    # --- Core Instructions and Rules ---
    prompt = f"""**Task:** Analyze the agricultural report text and extract information for each distinct operation described. Format the output as a JSON list, where each object in the list corresponds to one operation and strictly adheres to the provided JSON schema.

**Rules & Guidelines:**
1.  **Output Format:** MUST be a valid JSON list `[...]`. Each element must be a JSON object `{...}` matching the schema.
2.  **One Object Per Operation:** If the input text describes multiple operations (often separated by newlines or specific phrasing), create a separate JSON object for EACH operation in the output list.
3.  **Contextual Inheritance:** If a `date` or `subdivision` is mentioned at the beginning of the text, apply it to all subsequent operations in that message, UNLESS a specific operation block explicitly mentions a different date or subdivision.
4.  **Data Extraction:**
    *   `date`: Extract dates. Recognize formats like DD.MM, DD.MM.YYYY, DD.MM.YY. If only DD.MM is given, assume the current year. Clean suffixes like 'г.'.
    *   `subdivision`: Extract the primary farm subdivision name (e.g., АОР, Мир, ТСК, Восход, СП Коломейцево). Use the 'Reference - Known Subdivisions' list for normalization. Ignore specific department ('Отд') or production unit ('ПУ') numbers/names unless the main subdivision name is absent, then infer if possible.
    *   `operation`: Identify the agricultural operation. Normalize abbreviations or variations using the 'Reference - Known Operations' list (e.g., 'Предп культ' -> 'Предпосевная культивация', '2-е диск' -> 'Дискование 2-е').
    *   `crop`: Identify the crop. Normalize abbreviations or variations using the 'Reference - Known Crops' list (e.g., 'оз пш' -> 'Пшеница озимая товарная', 'сах св' -> 'Свекла сахарная').
    *   `daily_area`, `total_area`: Extract values associated with 'га'. If presented as 'X/Y га', map X to `daily_area` and Y to `total_area`. If only one number is given with 'га', try to determine if it's daily or total based on context (often daily if not specified), otherwise assign it to `daily_area`.
    *   `daily_yield`, `total_yield`: Extract values associated with 'Вал' or 'ц'. If presented as 'Вал X/Y', map X to `daily_yield` and Y to `total_yield`. **IMPORTANT**: Yield values (Вал) are often large; assume they are in kg and divide them by 100.0 to get centners (ц) for the JSON output (e.g., input '1259680' becomes output 12596.80).
5.  **Normalization:** STRICTLY use the provided reference lists (Subdivisions, Operations, Crops) to normalize the extracted text into the standard terms before putting them in the JSON output.
6.  **Ignore Irrelevant Info:** DO NOT extract information unrelated to the schema fields, such as: number of machines ('агрегата'), rainfall ('Осадки'), yield per hectare ('Урожайность'), quality metrics ('Дигестия', 'Оз'), percentages (%), remaining area ('остаток'), notes, etc.
7.  **Completeness:** Fill all required fields (`date`, `subdivision`, `operation`, `crop`) in the JSON schema. If a value cannot be reliably extracted or inferred for a required field, make a best guess based on context or the lists. For optional fields (`daily_area`, `total_area`, `daily_yield`, `total_yield`), use `null` if the information is missing.

**JSON Schema:**
```json
{schema}
```

**Reference - Known Subdivisions:**
{', '.join(known_subdivisions_list) if known_subdivisions_list else 'Not available'}

**Reference - Known Operations:**
{', '.join(known_operations_list) if known_operations_list else 'Not available'}

**Reference - Known Crops:**
{', '.join(known_crops_list) if known_crops_list else 'Not available'}

**Examples:**
{few_shot_examples}

**Report Text to Analyze:**
'''{text}'''

**Extracted JSON List:**
"""

    # Add the user text
    prompt += f"\nReport Text to Analyze:\n'''{text}'''\n\nExtracted JSON List:"""
    
    return prompt

# --- Main Analysis Pipeline Class ---

class AnalysisPipeline:
    def __init__(self):
        if not MISTRAL_API_KEY:
            raise ValueError("MISTRAL_API_KEY environment variable not set.")
            
        # Simple rate limiter (e.g., 1 request per second) - adjust as needed
        self.rate_limiter = RateLimiter(rate=1, per=1) 
        self.client = MistralAnalysisClient(api_key=MISTRAL_API_KEY, rate_limiter=self.rate_limiter)
        self.extra_data = load_extra_data(EXTRA_DATA_PATH)
        self.model_schema = AgriculturalOperation.get_schema_for_prompt()

    def analyze_text(self, text: str) -> List[AgriculturalOperation]:
        """
        Analyzes the input text using the Mistral client and returns a list of structured AgriculturalOperation objects.
        """
        prompt = construct_prompt(text, self.model_schema, self.extra_data)
        # logger.debug(f"Constructed Prompt:\n{prompt}") # Keep commented unless debugging prompt issues

        try:
            response_data = self.client.analyze(text=text, prompt=prompt) # Pass constructed prompt
            
            if not response_data or "error" in response_data:
                logger.error(f"Analysis failed or returned error: {response_data}")
                return [] 

            # --- Response Parsing and Validation ---
            # Expecting a JSON list directly based on the updated prompt instructions.
            
            operations_data = []
            if isinstance(response_data, list):
                 operations_data = response_data
            # Handle case where LLM might still wrap it, e.g. {"operations": [...]}
            elif isinstance(response_data, dict) and len(response_data) == 1:
                 key = list(response_data.keys())[0]
                 if isinstance(response_data[key], list):
                     logger.warning(f"LLM returned a dict with key '{key}' containing the list, instead of a direct list.")
                     operations_data = response_data[key]
                 else:
                     # Could potentially be a single object not in a list - try processing it
                      logger.warning(f"LLM returned a dict but expected a list. Attempting to process as single object.")
                      operations_data = [response_data] 
            else:
                 logger.error(f"Unexpected response format from LLM. Expected list, got {type(response_data)}: {response_data}")
                 return []


            validated_operations = []
            current_year = date.today().year # Get current year once
            for op_data in operations_data:
                if not isinstance(op_data, dict):
                    logger.warning(f"Skipping item in response list as it's not a dictionary: {op_data}")
                    continue
                    
                try:
                    # --- Date Handling ---
                    if 'date' in op_data and isinstance(op_data['date'], str):
                         op_date_str = op_data['date'].strip().replace('г.', '') # Clean up date string
                         parts = op_date_str.split('.')
                         try:
                             if len(parts) == 2:
                                 day, month = map(int, parts)
                                 # Assume current year if only day and month provided
                                 op_data['date'] = date(current_year, month, day).isoformat()
                             elif len(parts) == 3:
                                 day, month, year = map(int, parts)
                                 # Handle 2-digit year (e.g., 25 -> 2025)
                                 if year < 100: 
                                     year += 2000 
                                 op_data['date'] = date(year, month, day).isoformat()
                             else:
                                 logger.warning(f"Could not parse date format: {op_data['date']}")
                                 op_data['date'] = None # Set to None if parsing fails
                         except ValueError:
                             logger.warning(f"Invalid date components found: {op_data['date']}")
                             op_data['date'] = None
                    elif 'date' not in op_data or op_data.get('date') is None:
                         # Explicitly set to None if missing or already None
                         op_data['date'] = None 

                    # --- Yield Handling (Potential Division) ---
                    # Example: If 'Вал' comes as '1259680' and means 12596.80 centners
                    # Adjust this factor based on actual data meaning. Factor 100 assumes input is 100*centners (e.g., kg?)
                    yield_division_factor = 100.0 
                    if 'daily_yield' in op_data and isinstance(op_data['daily_yield'], (int, float)) and op_data['daily_yield'] > 10000: # Heuristic check
                         op_data['daily_yield'] /= yield_division_factor
                    if 'total_yield' in op_data and isinstance(op_data['total_yield'], (int, float)) and op_data['total_yield'] > 10000: # Heuristic check
                         op_data['total_yield'] /= yield_division_factor

                    # --- Area Handling (Ensure Float) ---
                    # Pydantic should handle string->float conversion if possible, but explicit is safer
                    if 'daily_area' in op_data and isinstance(op_data['daily_area'], str):
                        try: op_data['daily_area'] = float(op_data['daily_area'].replace(',', '.')) 
                        except ValueError: op_data['daily_area'] = None
                    if 'total_area' in op_data and isinstance(op_data['total_area'], str):
                         try: op_data['total_area'] = float(op_data['total_area'].replace(',', '.'))
                         except ValueError: op_data['total_area'] = None


                    operation = AgriculturalOperation.model_validate(op_data)
                    validated_operations.append(operation)
                except ValidationError as e:
                    logger.error(f"Pydantic Validation Error for operation data {op_data}: {e}")
                except (ValueError, TypeError, KeyError) as e: # Catch potential type/key errors during processing
                     logger.error(f"Data type, format, or key error during processing {op_data}: {e}")

            return validated_operations

        except MistralException as e:
            logger.error(f"Mistral API error during analysis: {e}")
            return []
        except Exception as e:
            logger.exception(f"Unexpected error during analysis pipeline: {e}") # Log full traceback
            return []

# --- Example Usage (for testing) ---
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Ensure MISTRAL_API_KEY is set as an environment variable for this test
    if not os.getenv("MISTRAL_API_KEY"):
        print("Error: MISTRAL_API_KEY environment variable is not set.")
        # Set a dummy key for basic structure check if needed, but API call will fail
        # os.environ["MISTRAL_API_KEY"] = "YOUR_DUMMY_KEY_HERE" 
        # exit(1) # Exit if key is absolutely required for testing flow

    pipeline = AnalysisPipeline()

    # Example texts from the HTML file
    test_texts = [
        "Пахота зяби под сою", # Example 1 (Implies multiple operations)
        "Уборка свеклы 27.10.день", # Example 2 (Single operation with date and yield)
        "20.11 Мир", # Example 3 (Implies multiple operations with different dates)
        "Внесение удобрений под рапс отд 7 -136/270", # Example 5 from image (Needs interpretation)
        "Север" # Example 4 from image (Seems incomplete?)
    ]

    for text in test_texts:
        print(f"\n--- Analyzing Text: '{text}' ---")
        results = pipeline.analyze_text(text)
        if results:
            for result in results:
                print(result.model_dump_json(indent=2))
        else:
            print("Analysis returned no results or failed.")
