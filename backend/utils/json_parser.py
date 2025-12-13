"""JSON parsing utilities."""
import json
import re
from typing import Any, Dict, List, Optional

def clean_and_parse_json(text: str) -> Optional[Dict[str, Any]]:
    """Clean and parse JSON from text that may contain markdown code blocks."""
    # Remove markdown code blocks
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    text = re.sub(r'```\w*\s*', '', text)
    
    # Find JSON object or array
    json_match = re.search(r'\{.*\}|\[.*\]', text, re.DOTALL)
    if json_match:
        text = json_match.group(0)
    
    # Try to parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to fix common issues
        text = text.strip()
        # Remove trailing commas
        text = re.sub(r',\s*}', '}', text)
        text = re.sub(r',\s*]', ']', text)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

