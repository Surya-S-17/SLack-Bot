import re
from datetime import datetime

def extract_date_and_amount2(text):
    # Define regex pattern for various date formats
    date_pattern = r'(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4})|(?:\d{4}[/-]\d{1,2}[/-]\d{1,2})|(?:\d{1,2}-\w{3}-\d{2,4})|(?:\d{2}-\w{3}-\d{4})|(?:\d{4}-\d{1,2}-\d{1,2})|(?:\d{1,2}\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[a-z]*\s+\d{2,4})'

    # Find the "Net Total (Including Taxes)" line
    net_total_line = re.search(r'Net Total \(Including Taxes\):\s*(\$?\d+(?:[.,]\d+)?)', text)

    # Extract date
    date_match = re.search(date_pattern, text, re.IGNORECASE)
    extracted_date = date_match.group() if date_match else None

    # Extract amount from "Net Amount" if "Net Total" line is not found
    if net_total_line:
        extracted_amount = net_total_line.group(1)
    else:
        # Look for amount in the text
        amount_match = re.search(r'(?:Grand\s+)?Total\s*[:₹]?\s*(\$?\d+(?:[.,]\d+)?)', text)
        extracted_amount = amount_match.group(1) if amount_match else None

    # Normalize date format if possible
    if extracted_date:
        extracted_date = normalize_date(extracted_date)

    return extracted_date, extracted_amount
def extract_amount(text):
    net_total_line = re.search(r'Net Total \(Including Taxes\):\s*(\$?\d+(?:[.,]\d+)?)', text)
    # Extract amount from "Net Amount" if "Net Total" line is not found
    if net_total_line:
        extracted_amount = net_total_line.group(1)
    else:
        # Look for amount in the text
        amount_match = re.search(r'(?:Grand\s+)?Total\s*[:₹]?\s*(\$?\d+(?:[.,]\d+)?)', text)
        extracted_amount = amount_match.group(1) if amount_match else None
    return extracted_amount

def extract_date(text):
    # Define regex pattern for various date formats
    date_pattern = r'(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4})|(?:\d{4}[/-]\d{1,2}[/-]\d{1,2})|(?:\d{1,2}-\w{3}-\d{2,4})|(?:\d{2}-\w{3}-\d{4})|(?:\d{4}-\d{1,2}-\d{1,2})|(?:\d{1,2}\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[a-z]*\s+\d{2,4})'

    # Extract date
    date_match = re.search(date_pattern, text, re.IGNORECASE)
    extracted_date = date_match.group() if date_match else None

    # Normalize date format if possible
    if extracted_date:
        extracted_date = normalize_date(extracted_date)
    return extracted_date

def normalize_date(date_str):
    try:
        # Try parsing the date with various formats
        date_formats = ['%d-%b-%Y', '%d/%m/%y', '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y', '%Y-%m-%d', '%d %B %Y', '%B %d, %Y', '%m/%d/%y', '%d/%m/%y', '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y', '%d %B %Y', '%B %d, %Y', '%B %d, %Y', '%m/%d/%y', '%Y %B %d']
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                pass
        return date_str  # Return original if no match found
    except Exception as e:
        print("Error:", e)
        return None

