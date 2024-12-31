import re
import json
import logging

def match_patterns(text, patterns):
    """
    Extracts and parses data from HTML based on the given patterns.
    
    Parameters:
        text (str): The HTML content to parse.
        patterns (list): A list of dictionaries with 'key' and 'pattern'.
    
    Returns:
        dict: A dictionary with extracted data.
    """
    extracted_data = {}

    for item in patterns:
        try:
            match = re.search(item["pattern"], text, re.DOTALL)
            if match:
                content = match.group(1).strip()
                if content.startswith("{") or content.startswith("["):
                    try:
                        extracted_data[item["key"]] = json.loads(content)
                    except json.JSONDecodeError as e:
                        logging.error(f"Error decoding JSON for {item['key']}: {e}")
                        extracted_data[item["key"]] = content  # Fallback to raw string
                else:
                    extracted_data[item["key"]] = content
        except Exception as e:
            logging.error(f"Error processing pattern for {item['key']}: {e}")
            extracted_data[item["key"]] = None
    
    return extracted_data
