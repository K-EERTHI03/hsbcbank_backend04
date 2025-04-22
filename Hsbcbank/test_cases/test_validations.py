
import unittest
from utils import validate_card_number, validate_name, validate_zip_code, validate_date
from utils import validate_amount, validate_currency, validate_email, validate_cvv
from utils import validate_expiry_date, validate_language

class TestValidations(unittest.TestCase):
    def test_card_number(self):
        self.assertTrue(validate_card_number("1234567890123456"))
        self.assertFalse(validate_card_number("123-456-789"))
        self.assertFalse(validate_card_number("12345"))

    def test_name(self):
        self.assertTrue(validate_name("John Doe"))
        self.assertFalse(validate_name("J"))
        self.assertFalse(validate_name("A" * 41))

    def test_zip_code(self):
        self.assertTrue(validate_zip_code("12345"))
        self.assertTrue(validate_zip_code("123456"))
        self.assertFalse(validate_zip_code("1234"))

    def test_amount(self):
        self.assertTrue(validate_amount("100.50"))
        self.assertTrue(validate_amount("1000"))
        self.assertFalse(validate_amount("-50.00"))

    def test_currency(self):
        self.assertTrue(validate_currency("INR"))
        self.assertTrue(validate_currency("USD"))
        self.assertFalse(validate_currency("ABC"))

    def test_email(self):
        self.assertTrue(validate_email("test@example.com"))
        self.assertFalse(validate_email("invalid.email"))

    def test_language(self):
        self.assertTrue(validate_language("en"))
        self.assertTrue(validate_language("ta"))
        self.assertTrue(validate_language("hi"))
        self.assertFalse(validate_language("fr"))
        
    def test_date(self):
        self.assertTrue(validate_date("2024-04-15"))
        self.assertFalse(validate_date("15-04-2024"))
        self.assertFalse(validate_date("invalid"))
        
    def test_cvv(self):
        self.assertTrue(validate_cvv("123"))
        self.assertTrue(validate_cvv("1234"))
        self.assertFalse(validate_cvv("12"))
        self.assertFalse(validate_cvv("12345"))
        
    def test_expiry_date(self):
        self.assertTrue(validate_expiry_date("12/24"))
        self.assertFalse(validate_expiry_date("13/24"))
        self.assertFalse(validate_expiry_date("12/23"))

if __name__ == '__main__':
    unittest.main()
