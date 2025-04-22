from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Cardholder(Base):
    __tablename__ = 'cardholders'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    card_number = Column(String(20))
    billing_address = Column(String(200))
    email = Column(String(100))
    phone = Column(String(20))

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    cardholder_id = Column(Integer)
    date = Column(Date)
    description = Column(String(200))
    amount = Column(Float)

class Statement(Base):
    __tablename__ = 'statements'
    
    id = Column(Integer, primary_key=True)
    cardholder_id = Column(Integer)
    statement_date = Column(Date)
    previous_balance = Column(Float)
    payments_received = Column(Float)
    purchases_charges = Column(Float)
    finance_charges = Column(Float)
    new_balance = Column(Float)
    credit_limit = Column(Float)
    available_credit = Column(Float)
    payment_due_date = Column(Date)
    reward_points = Column(Integer)