"""Markdown to LaTeX conversion utilities."""
from typing import Optional

def create_latex_document(markdown_content: str, title: Optional[str] = None) -> str:
    """Convert markdown content to LaTeX document."""
    # Basic LaTeX document structure
    latex = "\\documentclass{article}\n"
    latex += "\\usepackage[utf8]{inputenc}\n"
    latex += "\\usepackage{graphicx}\n"
    latex += "\\usepackage{hyperref}\n"
    latex += "\\begin{document}\n"
    
    if title:
        latex += f"\\title{{{title}}}\n"
        latex += "\\maketitle\n"
    
    # Simple markdown to LaTeX conversion
    lines = markdown_content.split('\n')
    for line in lines:
        if line.startswith('# '):
            latex += f"\\section{{{line[2:]}}}\n"
        elif line.startswith('## '):
            latex += f"\\subsection{{{line[3:]}}}\n"
        elif line.startswith('### '):
            latex += f"\\subsubsection{{{line[4:]}}}\n"
        elif line.strip().startswith('*') or line.strip().startswith('-'):
            latex += f"\\begin{{itemize}}\n\\item {line.lstrip('*- ')}\n\\end{{itemize}}\n"
        else:
            latex += line + "\n"
    
    latex += "\\end{document}\n"
    return latex

