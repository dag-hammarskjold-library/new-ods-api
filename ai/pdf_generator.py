"""
PDF Generator for Chatbot User Manual
Converts markdown user manual to PDF format
"""

import os
import sys
from pathlib import Path

# Try to import markdown conversion libraries
try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False

# Try to import PDF generation libraries
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from markdown import markdown as md_to_html
    from html.parser import HTMLParser
    import re
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def markdown_to_pdf_reportlab(markdown_content: str, output_path: str) -> bool:
    """
    Convert markdown to PDF using ReportLab.
    
    Args:
        markdown_content: Markdown content as string
        output_path: Path where PDF should be saved
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Convert markdown to HTML first (not used in ReportLab version, but kept for consistency)
        # html_content = markdown.markdown(markdown_content, extensions=['extra', 'tables', 'codehilite'])
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor='#2c3e50',
            spaceAfter=12,
        )
        
        heading1_style = ParagraphStyle(
            'CustomHeading1',
            parent=styles['Heading1'],
            fontSize=16,
            textColor='#34495e',
            spaceAfter=10,
        )
        
        heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=styles['Heading2'],
            fontSize=14,
            textColor='#34495e',
            spaceAfter=8,
        )
        
        # Parse HTML and convert to ReportLab elements
        # Simple HTML parser for basic markdown elements
        lines = markdown_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                story.append(Spacer(1, 0.1*inch))
                continue
            
            # Headers
            if line.startswith('# '):
                text = line[2:].strip()
                story.append(Paragraph(text, title_style))
                story.append(Spacer(1, 0.2*inch))
            elif line.startswith('## '):
                text = line[3:].strip()
                story.append(Paragraph(text, heading1_style))
                story.append(Spacer(1, 0.15*inch))
            elif line.startswith('### '):
                text = line[4:].strip()
                story.append(Paragraph(text, heading2_style))
                story.append(Spacer(1, 0.1*inch))
            elif line.startswith('#### '):
                text = line[5:].strip()
                story.append(Paragraph(f"<b>{text}</b>", styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            # Lists
            elif line.startswith('- ') or line.startswith('* '):
                text = line[2:].strip()
                story.append(Paragraph(f"• {text}", styles['Normal']))
            elif line.startswith('  - ') or line.startswith('  * '):
                text = line[4:].strip()
                story.append(Paragraph(f"  ◦ {text}", styles['Normal']))
            # Code blocks (skip for now)
            elif line.startswith('```'):
                continue
            # Horizontal rule
            elif line.startswith('---'):
                story.append(Spacer(1, 0.2*inch))
            else:
                # Regular paragraph
                try:
                    # Escape HTML and convert markdown links
                    text = line
                    # Escape special characters for ReportLab
                    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    # Convert markdown links [text](url) to plain text (remove links to avoid ReportLab errors)
                    text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'\1', text)
                    # Convert bold **text** to <b>text</b>
                    text = re.sub(r'\*\*([^\*]+)\*\*', r'<b>\1</b>', text)
                    # Convert italic *text* to <i>text</i> (but not if it's part of bold)
                    text = re.sub(r'(?<!\*)\*([^\*]+)\*(?!\*)', r'<i>\1</i>', text)
                    # Convert inline code `code` to <font face="Courier">code</font>
                    text = re.sub(r'`([^`]+)`', r'<font face="Courier">\1</font>', text)
                    
                    story.append(Paragraph(text, styles['Normal']))
                    story.append(Spacer(1, 0.1*inch))
                except Exception as e:
                    # If paragraph creation fails, add as plain text
                    print(f"Warning: Could not format line as paragraph: {line[:50]}... Error: {e}", file=sys.stderr)
                    try:
                        story.append(Paragraph(line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), styles['Normal']))
                        story.append(Spacer(1, 0.1*inch))
                    except:
                        # Skip problematic lines
                        pass
        
        # Build PDF
        if not story:
            print("Error: No content to add to PDF", file=sys.stderr)
            return False
        
        doc.build(story)
        return True
        
    except Exception as e:
        print(f"Error generating PDF with ReportLab: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False


def markdown_to_pdf_weasyprint(markdown_content: str, output_path: str) -> bool:
    """
    Convert markdown to PDF using WeasyPrint.
    
    Args:
        markdown_content: Markdown content as string
        output_path: Path where PDF should be saved
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Convert markdown to HTML
        html_content = markdown.markdown(markdown_content, extensions=['extra', 'tables', 'codehilite', 'fenced_code'])
        
        # Add CSS styling
        css_content = """
        @page {
            size: A4;
            margin: 2cm;
        }
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
        }
        h3 {
            color: #34495e;
        }
        code {
            background-color: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        pre {
            background-color: #f4f4f4;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #3498db;
            color: white;
        }
        """
        
        # Wrap HTML with style
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>{css_content}</style>
        </head>
        <body>
        {html_content}
        </body>
        </html>
        """
        
        # Generate PDF
        HTML(string=full_html).write_pdf(output_path)
        return True
        
    except Exception as e:
        print(f"Error generating PDF with WeasyPrint: {e}", file=sys.stderr)
        return False


def generate_user_manual_pdf(output_path: str = None) -> str:
    """
    Generate PDF from the chatbot user manual markdown file.
    
    Args:
        output_path: Optional path for output PDF. If None, uses default location.
        
    Returns:
        str: Path to generated PDF file, or None if failed
    """
    try:
        # Get the manual markdown file
        ai_dir = Path(__file__).parent
        manual_path = ai_dir / "CHATBOT_USER_MANUAL.md"
        
        if not manual_path.exists():
            print(f"User manual not found at: {manual_path}", file=sys.stderr)
            return None
        
        # Read markdown content
        with open(manual_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Determine output path
        if output_path is None:
            output_path = ai_dir / "CHATBOT_USER_MANUAL.pdf"
        else:
            output_path = Path(output_path)
        
        # Convert to absolute path
        output_path = output_path.resolve()
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Try WeasyPrint first (better HTML/CSS support)
        if WEASYPRINT_AVAILABLE and MARKDOWN_AVAILABLE:
            if markdown_to_pdf_weasyprint(markdown_content, str(output_path)):
                return str(output_path.resolve())
        
        # Fallback to ReportLab
        if REPORTLAB_AVAILABLE and MARKDOWN_AVAILABLE:
            if markdown_to_pdf_reportlab(markdown_content, str(output_path)):
                return str(output_path.resolve())
        
        # If no PDF library available, return error
        print("No PDF generation library available. Install with: pip install weasyprint markdown", file=sys.stderr)
        return None
        
    except Exception as e:
        print(f"Error generating PDF: {e}", file=sys.stderr)
        return None


def generate_ods_documentation_pdf(output_path: str = None) -> str:
    """
    Generate PDF from the extracted documentation text file.
    
    Args:
        output_path: Optional path for output PDF. If None, uses default location.
        
    Returns:
        str: Path to generated PDF file, or None if failed
    """
    try:
        # Get the documentation text file
        ai_dir = Path(__file__).parent
        doc_path = ai_dir / "extracted_documentation.txt"
        
        if not doc_path.exists():
            print(f"Documentation file not found at: {doc_path}", file=sys.stderr)
            return None
        
        # Read text content
        with open(doc_path, 'r', encoding='utf-8') as f:
            text_content = f.read()
        
        # Determine output path
        if output_path is None:
            output_path = ai_dir / "ODS_Actions_Documentation.pdf"
        else:
            output_path = Path(output_path)
        
        # Convert to absolute path
        output_path = output_path.resolve()
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Try WeasyPrint first (better HTML/CSS support)
        if WEASYPRINT_AVAILABLE and MARKDOWN_AVAILABLE:
            # Convert plain text to markdown-like format for better rendering
            # Add basic markdown formatting
            markdown_content = text_content
            # Convert (cid:127) to bullet points
            markdown_content = markdown_content.replace('(cid:127)', '- ')
            # Add some basic formatting
            lines = markdown_content.split('\n')
            formatted_lines = []
            for line in lines:
                # Format section headers
                if line.strip() and not line.startswith(' ') and not line.startswith('-') and len(line) < 100:
                    if line.isupper() or (line and line[0].isupper() and ':' not in line and line.count(' ') < 5):
                        formatted_lines.append(f"## {line}")
                    else:
                        formatted_lines.append(line)
                else:
                    formatted_lines.append(line)
            markdown_content = '\n'.join(formatted_lines)
            
            if markdown_to_pdf_weasyprint(markdown_content, str(output_path)):
                return str(output_path.resolve())
        
        # Fallback to ReportLab
        if REPORTLAB_AVAILABLE:
            # Convert plain text to markdown-like format
            markdown_content = text_content.replace('(cid:127)', '- ')
            if markdown_to_pdf_reportlab(markdown_content, str(output_path)):
                return str(output_path.resolve())
        
        # If no PDF library available, return error
        print("No PDF generation library available. Install with: pip install weasyprint markdown", file=sys.stderr)
        return None
        
    except Exception as e:
        print(f"Error generating PDF: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "ods":
        # Generate ODS Actions Documentation PDF
        print("Generating ODS Actions Documentation PDF...")
        result = generate_ods_documentation_pdf()
        if result:
            print(f"PDF generated successfully: {result}")
        else:
            print("Failed to generate PDF")
            print("\nPlease install required libraries:")
            print("  pip install weasyprint markdown  # Recommended")
            print("  OR")
            print("  pip install reportlab markdown")
    else:
        # Test PDF generation for user manual
        print("Generating PDF from user manual...")
        result = generate_user_manual_pdf()
        if result:
            print(f"PDF generated successfully: {result}")
        else:
            print("Failed to generate PDF")
            print("\nPlease install required libraries:")
            print("  pip install weasyprint markdown  # Recommended")
            print("  OR")
            print("  pip install reportlab markdown")

