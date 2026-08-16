import os
import re
from typing import Dict, List, Any, Tuple
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET


def clean_html(html_text: str) -> str:
    """
    Clean HTML text by removing tags and formatting.
    
    Args:
        html_text: HTML text to clean
        
    Returns:
        Cleaned text
    """
    soup = BeautifulSoup(html_text, 'html.parser')
    return soup.get_text(separator=' ', strip=True)


def parse_xbrl(xbrl_file: str) -> Dict[str, Any]:
    """
    Parse XBRL file to extract financial data.
    
    Args:
        xbrl_file: Path to XBRL file
        
    Returns:
        Extracted financial data as a dictionary
    """
    try:
        tree = ET.parse(xbrl_file)
        root = tree.getroot()
        
        # Create namespaces dictionary
        namespaces = {
            'xbrli': 'http://www.xbrl.org/2003/instance',
            'ix': 'http://www.xbrl.org/2013/inlineXBRL',
            'us-gaap': 'http://fasb.org/us-gaap/2019-01-31'
        }
        
        # Extract relevant financial data
        data = {}
        
        # Common financial metrics to extract
        metrics = [
            'Assets', 'Liabilities', 'StockholdersEquity', 'Revenue', 
            'CostOfRevenue', 'GrossProfit', 'OperatingIncome', 
            'NetIncome', 'EarningsPerShare', 'DividendsPerShare'
        ]
        
        # Try to extract each metric
        for metric in metrics:
            try:
                # Try different namespace variations
                for ns in ['us-gaap', 'dei', 'xbrli']:
                    try:
                        elements = root.findall(f'.//{{{namespaces.get(ns, "")}}}:{metric}', namespaces)
                        if elements:
                            data[metric] = elements[0].text
                            break
                    except:
                        continue
            except:
                continue
        
        return data
    except Exception as e:
        print(f"Error parsing XBRL file: {e}")
        return {}


def extract_text_from_filing(filing_path: str) -> str:
    """
    Extract text content from SEC filing.
    
    Args:
        filing_path: Path to filing
        
    Returns:
        Extracted text
    """
    # Determine file type
    if filing_path.endswith('.xml') or filing_path.endswith('.xbrl'):
        return extract_text_from_xbrl(filing_path)
    elif filing_path.endswith('.htm') or filing_path.endswith('.html'):
        return extract_text_from_html(filing_path)
    else:
        with open(filing_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()


def extract_text_from_xbrl(file_path: str) -> str:
    """
    Extract text content from XBRL file.
    
    Args:
        file_path: Path to XBRL file
        
    Returns:
        Extracted text
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Extract all text content
        text_content = []
        
        # Extract text from all elements
        for elem in root.iter():
            if elem.text and elem.text.strip():
                text_content.append(elem.text.strip())
        
        return ' '.join(text_content)
    except Exception as e:
        print(f"Error extracting text from XBRL: {e}")
        return ""


def extract_text_from_html(file_path: str) -> str:
    """
    Extract text content from HTML file.
    
    Args:
        file_path: Path to HTML file
        
    Returns:
        Extracted text
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        
        # Get text
        text = soup.get_text(separator=' ', strip=True)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    except Exception as e:
        print(f"Error extracting text from HTML: {e}")
        return ""


def format_number(num: Any) -> str:
    """
    Format a number for display.
    
    Args:
        num: Number to format
        
    Returns:
        Formatted number string
    """
    try:
        if isinstance(num, str):
            num = float(num.replace(',', ''))
        
        if num >= 1_000_000_000:
            return f"${num / 1_000_000_000:.2f}B"
        elif num >= 1_000_000:
            return f"${num / 1_000_000:.2f}M"
        elif num >= 1_000:
            return f"${num / 1_000:.2f}K"
        else:
            return f"${num:.2f}"
    except:
        return str(num)