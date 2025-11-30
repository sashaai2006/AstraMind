import json
import re
from typing import Any, Dict, Union

def clean_and_parse_json(text: str) -> Union[Dict[str, Any], list]:
    """
    Robustly extracts and parses JSON from a string, handling common LLM artifacts
    like Markdown code blocks, unescaped newlines, and conversational fluff.
    """
    # 1. Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2. Extract from Markdown code blocks ```json ... ```
    json_block_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    matches = re.findall(json_block_pattern, text)
    
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            # Try to repair common issues within the block
            try:
                return _repair_and_parse(match)
            except Exception:
                continue

    # 3. Try to find the first { and last } (if no markdown blocks)
    try:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            potential_json = text[start : end + 1]
            return json.loads(potential_json)
    except json.JSONDecodeError:
        pass

    # 4. Last resort: aggressive repair on the whole text or extracted block
    # Often LLMs put newlines in strings without escaping them.
    try:
        return _repair_and_parse(text)
    except Exception:
        pass

    raise ValueError("Failed to parse JSON from text")


def _repair_and_parse(json_str: str) -> Any:
    """
    Attempt to fix common JSON errors from LLMs:
    1. Unescaped newlines in double quotes.
    2. Trailing commas.
    """
    # Simple heuristic to escape newlines inside string values
    # This is risky but often necessary for generated code files.
    # We iterate through the string and toggle "in_string" state.
    
    # Note: Implementing a full streaming JSON parser is complex. 
    # For now, let's try a regex approach for specific bad patterns if needed,
    # or rely on the agents to be better prompted.
    
    # Let's try `strict=False` first
    try:
        return json.loads(json_str, strict=False)
    except json.JSONDecodeError:
        pass
        
    # Replace real newlines with \n if they seem to be inside content
    # This is a very naive patch for code generation
    # improved_str = json_str.replace("\n", "\\n") 
    # return json.loads(improved_str)
    
    raise ValueError("Could not repair JSON")

