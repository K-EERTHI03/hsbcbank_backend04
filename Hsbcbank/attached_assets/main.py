from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Cardholder, Transaction, Statement
from pdf_generator import StatementPDFGenerator
import datetime

def create_sample_statement(name, card_number, email, phone):
    # Create database engine
    engine = create_engine('sqlite:///credit_card.db')
    Base.metadata.create_all(engine)
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Create cardholder with user input
    cardholder = Cardholder(
        name=name,
        card_number=card_number,
        billing_address="D-45, Green Park,\nNew Delhi-110016, India",
        email=email,
        phone=phone
    )
    session.add(cardholder)
    session.commit()
    
    # Create sample transactions
    transactions = [
        Transaction(
            cardholder_id=cardholder.id,
            date=datetime.date(2025, 3, 2),
            description="Amazon India - Electronics",
            amount=3499.00
        ),
        Transaction(
            cardholder_id=cardholder.id,
            date=datetime.date(2025, 3, 2),
            description="Uber Ride - New Delhi",
            amount=285.50
        )
    ]
    session.add_all(transactions)
    
    # Create statement
    statement = Statement(
        cardholder_id=cardholder.id,
        statement_date=datetime.date(2025, 3, 31),
        previous_balance=13840.00,
        payments_received=175.50,
        purchases_charges=640.00,
        finance_charges=45.00,
        new_balance=13935.50,
        credit_limit=175.00,
        available_credit=1230.00,
        payment_due_date=datetime.date(2025, 4, 20),
        reward_points=175
    )
    session.add(statement)
    session.commit()
    
    # Generate PDF
    pdf_generator = StatementPDFGenerator(statement, cardholder, transactions)
    pdf_generator.generate_pdf('credit_card_statement.pdf')
    
    session.close()