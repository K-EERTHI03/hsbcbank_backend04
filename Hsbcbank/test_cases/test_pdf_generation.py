
import unittest
import os
from models import Cardholder, Transaction, Statement
from pdf_generator import StatementPDFGenerator
import datetime

class TestPDFGeneration(unittest.TestCase):
    def setUp(self):
        self.cardholder = Cardholder(
            name="Test User",
            card_number="1234567890123456",
            billing_address="123 Test St",
            email="test@example.com",
            phone="1234567890"
        )
        
        self.transactions = [
            Transaction(
                cardholder_id=1,
                date=datetime.date(2024, 4, 1),
                description="Test Purchase",
                amount=100.00
            )
        ]
        
        self.statement = Statement(
            cardholder_id=1,
            statement_date=datetime.date(2024, 4, 1),
            previous_balance=1000.00,
            payments_received=500.00,
            purchases_charges=100.00,
            finance_charges=10.00,
            new_balance=610.00,
            credit_limit=5000.00,
            available_credit=4390.00,
            payment_due_date=datetime.date(2024, 4, 21),
            reward_points=100
        )

    def test_english_pdf_generation(self):
        generator = StatementPDFGenerator(self.statement, self.cardholder, self.transactions, 'en')
        output_path = "test_en.pdf"
        generator.generate_pdf(output_path)
        self.assertTrue(os.path.exists(output_path))
        os.remove(output_path)

    def test_tamil_pdf_generation(self):
        generator = StatementPDFGenerator(self.statement, self.cardholder, self.transactions, 'ta')
        output_path = "test_ta.pdf"
        generator.generate_pdf(output_path)
        self.assertTrue(os.path.exists(output_path))
        os.remove(output_path)

    def test_hindi_pdf_generation(self):
        generator = StatementPDFGenerator(self.statement, self.cardholder, self.transactions, 'hi')
        output_path = "test_hi.pdf"
        generator.generate_pdf(output_path)
        self.assertTrue(os.path.exists(output_path))
        os.remove(output_path)

if __name__ == '__main__':
    unittest.main()
