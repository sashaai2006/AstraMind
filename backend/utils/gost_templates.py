"""GOST template utilities."""
from pathlib import Path
from typing import Optional

def get_gost_prompt_instructions(doc_type: str) -> str:
    """Get prompt instructions for GOST document type."""
    if doc_type == "gost_explanatory_note":
        return "Создайте пояснительную записку по ГОСТ"
    elif doc_type == "technical_assignment":
        return "Создайте техническое задание по ГОСТ"
    return ""

def get_gost_template_hint(doc_type: str) -> str:
    """Get template hint for GOST document type."""
    if doc_type == "gost_explanatory_note":
        return "Используйте шаблон пояснительной записки ГОСТ"
    elif doc_type == "technical_assignment":
        return "Используйте шаблон технического задания ГОСТ"
    return ""

def get_gost_explanatory_note_template() -> str:
    """Get GOST explanatory note template."""
    template_path = Path(__file__).parent.parent.parent / "documents" / "gost_explanatory_note_template.tex"
    if template_path.exists():
        return template_path.read_text(encoding='utf-8')
    return ""

def get_technical_assignment_template() -> str:
    """Get technical assignment template."""
    template_path = Path(__file__).parent.parent.parent / "documents" / "technical_assignment_template.tex"
    if template_path.exists():
        return template_path.read_text(encoding='utf-8')
    return ""

