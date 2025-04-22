import logging
import time
import os
import tempfile
import gc
import psutil
import datetime
import re

logger = logging.getLogger(__name__)

def get_memory_usage():
    """Get current memory usage of the process"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return {
        'rss': memory_info.rss / (1024 * 1024),  # RSS in MB
        'vms': memory_info.vms / (1024 * 1024)   # VMS in MB
    }

def format_currency(amount, currency_symbol='₹'):
    """Format a currency amount with the given symbol"""
    return f"{currency_symbol} {amount:,.2f}"

def format_date(date_obj, format_str='%d-%b-%Y'):
    """Format a date object to string"""
    if isinstance(date_obj, datetime.date):
        return date_obj.strftime(format_str)
    return str(date_obj)

def create_temp_file(suffix='.pdf'):
    """Create a temporary file and return its path"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    path = temp_file.name
    temp_file.close()
    return path

def clean_up_resources():
    """Force garbage collection and clean up resources"""
    gc.collect()
    return get_memory_usage()

def batch_process(items, batch_size=500, process_func=None):
    """Process a large list of items in batches"""
    results = []
    total_items = len(items)
    
    for i in range(0, total_items, batch_size):
        batch = items[i:i+batch_size]
        
        if process_func:
            batch_result = process_func(batch)
            if batch_result:
                results.extend(batch_result)
        else:
            results.extend(batch)
        
        # Force garbage collection after each batch
        gc.collect()
    
    return results

def validate_language(language_code, default='en'):
    """Validate if the language code is supported"""
    
    if language_code in ['en', 'ta', 'hi']:
        return language_code
    return default

def validate_card_number(card_number: str) -> bool:
    """Validate 16-digit card number"""
    return bool(re.match(r'^\d{16}$', card_number))

def validate_name(name: str) -> bool:
    """Validate name (2-40 chars, letters and spaces)"""
    return len(name) >= 2 and len(name) <= 40

def validate_zip_code(zip_code: str) -> bool:
    """Validate 5-6 digit ZIP code"""
    return bool(re.match(r'^\d{5,6}$', zip_code))

def validate_date(date_str: str) -> bool:
    """Validate YYYY-MM-DD date format"""
    try:
        datetime.datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_amount(amount: str) -> bool:
    """Validate positive amount with up to 2 decimal places"""
    try:
        float_amount = float(amount)
        return float_amount > 0
    except ValueError:
        return False

def validate_currency(currency: str) -> bool:
    """Validate currency code"""
    valid_currencies = ['USD', 'INR', 'GBP', 'EUR']
    return currency in valid_currencies

def validate_email(email: str) -> bool:
    """Validate email format"""
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))

def validate_cvv(cvv: str) -> bool:
    """Validate 3-digit CVV"""
    return bool(re.match(r'^\d{3,4}$', cvv))

def validate_expiry_date(expiry_date: str) -> bool:
    """Validate MM/YY expiry date format and not past date"""
    try:
        month, year = map(int, expiry_date.split('/'))
        return 1 <= month <= 12 and year >= 2024
    except (ValueError, IndexError):
        return False