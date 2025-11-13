"""
PDF Information Extractor for ODS Actions Documentation

This module extracts all text content from the ODS_Actions_Documentation.pdf
and makes it available for use by AI bots and other programs.
"""

import os
import sys
from pathlib import Path

# Try to import PDF libraries (will install if needed)
try:
    import pdfplumber
    PDF_LIBRARY = 'pdfplumber'
except ImportError:
    try:
        import PyPDF2
        PDF_LIBRARY = 'PyPDF2'
    except ImportError:
        try:
            import pypdf
            PDF_LIBRARY = 'pypdf'
        except ImportError:
            PDF_LIBRARY = None


def extract_pdf_content(pdf_path=None):
    """
    Extract all text content from the ODS Actions Documentation PDF.
    
    Args:
        pdf_path (str, optional): Path to the PDF file. 
                                  If None, uses default path: ../ODS_Actions_Documentation.pdf
    
    Returns:
        dict: Dictionary containing:
            - 'full_text' (str): Complete extracted text
            - 'pages' (list): List of text per page
            - 'metadata' (dict): PDF metadata if available
            - 'success' (bool): Whether extraction was successful
            - 'error' (str): Error message if extraction failed
    """
    
    # Default PDF path (relative to this file)
    if pdf_path is None:
        # Get the directory where this script is located
        script_dir = Path(__file__).parent
        # First try in the ai folder (where the PDF should be)
        pdf_path = script_dir / "ODS_Actions_Documentation.pdf"
        # If not found, try in parent directory
        if not pdf_path.exists():
            pdf_path = script_dir.parent / "ODS_Actions_Documentation.pdf"
    
    pdf_path = Path(pdf_path)
    
    result = {
        'full_text': '',
        'pages': [],
        'metadata': {},
        'success': False,
        'error': None,
        'pdf_path': str(pdf_path)
    }
    
    # Check if PDF exists
    if not pdf_path.exists():
        result['error'] = f"PDF file not found at: {pdf_path}"
        return result
    
    # Extract based on available library
    if PDF_LIBRARY == 'pdfplumber':
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Extract metadata
                result['metadata'] = {
                    'num_pages': len(pdf.pages),
                    'metadata': pdf.metadata or {}
                }
                
                # Extract text from each page
                full_text_parts = []
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        result['pages'].append({
                            'page_number': i + 1,
                            'text': page_text
                        })
                        full_text_parts.append(page_text)
                
                result['full_text'] = '\n\n'.join(full_text_parts)
                result['success'] = True
                
        except Exception as e:
            result['error'] = f"Error extracting PDF with pdfplumber: {str(e)}"
    
    elif PDF_LIBRARY == 'pypdf':
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                
                # Extract metadata
                result['metadata'] = {
                    'num_pages': len(pdf_reader.pages),
                    'metadata': pdf_reader.metadata or {}
                }
                
                # Extract text from each page
                full_text_parts = []
                for i, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        result['pages'].append({
                            'page_number': i + 1,
                            'text': page_text
                        })
                        full_text_parts.append(page_text)
                
                result['full_text'] = '\n\n'.join(full_text_parts)
                result['success'] = True
                
        except Exception as e:
            result['error'] = f"Error extracting PDF with pypdf: {str(e)}"
    
    elif PDF_LIBRARY == 'PyPDF2':
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract metadata
                result['metadata'] = {
                    'num_pages': len(pdf_reader.pages),
                    'metadata': pdf_reader.metadata or {}
                }
                
                # Extract text from each page
                full_text_parts = []
                for i, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        result['pages'].append({
                            'page_number': i + 1,
                            'text': page_text
                        })
                        full_text_parts.append(page_text)
                
                result['full_text'] = '\n\n'.join(full_text_parts)
                result['success'] = True
                
        except Exception as e:
            result['error'] = f"Error extracting PDF with PyPDF2: {str(e)}"
    
    else:
        result['error'] = "No PDF library available. Please install one of: pdfplumber, pypdf, or PyPDF2"
        result['error'] += "\nInstall with: pip install pdfplumber (recommended)"
    
    return result


def get_documentation_text():
    """
    Convenience function to get just the full text content.
    
    Returns:
        str: Full text content of the PDF, or empty string if extraction failed
    """
    result = extract_pdf_content()
    if result['success']:
        return result['full_text']
    else:
        print(f"Error extracting PDF: {result['error']}", file=sys.stderr)
        return ""


# Global variable to store extracted content (loaded on import)
_documentation_data = None


def load_documentation():
    """
    Load documentation data into global variable.
    This function is called automatically on import, but can be called
    manually to reload the data.
    
    Returns:
        dict: The extracted documentation data
    """
    global _documentation_data
    _documentation_data = extract_pdf_content()
    return _documentation_data


def get_documentation():
    """
    Get the loaded documentation data.
    If not loaded yet, loads it automatically.
    
    Returns:
        dict: The extracted documentation data
    """
    global _documentation_data
    if _documentation_data is None:
        _documentation_data = load_documentation()
    return _documentation_data


# Auto-load documentation on import
try:
    _documentation_data = extract_pdf_content()
except Exception as e:
    print(f"Warning: Could not auto-load documentation: {e}", file=sys.stderr)
    _documentation_data = None


# Export the documentation text as a module-level variable
DOCUMENTATION_TEXT = get_documentation_text()
DOCUMENTATION_DATA = get_documentation()


if __name__ == "__main__":
    # Test the extraction
    print("Extracting PDF content...")
    print(f"PDF Library: {PDF_LIBRARY}")
    print("-" * 50)
    
    data = extract_pdf_content()
    
    if data['success']:
        print(f"✓ Successfully extracted {data['metadata'].get('num_pages', 0)} pages")
        print(f"✓ Total text length: {len(data['full_text'])} characters")
        print(f"✓ Number of pages: {len(data['pages'])}")
        print("\nFirst 500 characters:")
        print("-" * 50)
        print(data['full_text'][:500])
        print("...")
        print("\n✓ Documentation data is available via:")
        print("  - DOCUMENTATION_TEXT (string)")
        print("  - DOCUMENTATION_DATA (dict)")
        print("  - get_documentation() function")
    else:
        print(f"✗ Error: {data['error']}")
        print("\nPlease install a PDF library:")
        print("  pip install pdfplumber  # Recommended")
        print("  pip install pypdf")
        print("  pip install PyPDF2")

