from models import Base, Cardholder, Transaction, Statement
from pdf_generator import StatementPDFGenerator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
import os
import shutil  # Import shutil for directory operations
# Create output directory or clear it if it exists
output_dir = 'sample_output'  # Updated to the desired folder name
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)  # Clear the existing directory
os.makedirs(output_dir)  # Create a new directory
# Database setup
engine = create_engine('sqlite:///credit_card.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
# Create sample cardholder
cardholder = Cardholder(
    name="John Doe",
    card_number="1234567890123456",
    billing_address="123 Sample St, City, Country",
    email="john@example.com",
    phone="1234567890"
)
session.add(cardholder)
session.commit()  # Commit this to get cardholder.id
# Create sample transactions
transactions = [
    Transaction(
        cardholder_id=cardholder.id,
        date=datetime.date(2025, 3, 2),
        description="Amazon Purchase",
        amount=1500.00
    ),
    Transaction(
        cardholder_id=cardholder.id,
        date=datetime.date(2025, 3, 3),
        description="Restaurant Bill",
        amount=2500.00
    )
]
session.add_all(transactions)
session.commit()
# Create statement
statement = Statement(
    cardholder_id=cardholder.id,
    statement_date=datetime.date.today(),
    previous_balance=10000.00,
    payments_received=5000.00,
    purchases_charges=4000.00,
    finance_charges=100.00,
    new_balance=9100.00,
    credit_limit=50000.00,
    available_credit=40900.00,
    payment_due_date=datetime.date.today() + datetime.timedelta(days=21),
    reward_points=175
)
session.add(statement)
session.commit()
# Generate PDFs in different languages
languages = ['en', 'ta', 'hi']
for lang in languages:
    generator = StatementPDFGenerator(statement, cardholder, transactions, lang)
    output_path = f"{output_dir}/statement_{lang}.pdf"
    generator.generate_pdf(output_path)
    print(f"Generated {output_path}")
session.close()
print("Sample generation complete!")