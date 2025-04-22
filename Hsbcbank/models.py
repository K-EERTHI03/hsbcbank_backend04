from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Cardholder(Base):
    __tablename__ = 'cardholders'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    card_number = Column(String(20))
    billing_address = Column(String(200))
    email = Column(String(100))
    phone = Column(String(20))
    
    transactions = relationship("Transaction", back_populates="cardholder")
    statements = relationship("Statement", back_populates="cardholder")

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    cardholder_id = Column(Integer, ForeignKey('cardholders.id'))
    date = Column(Date)
    description = Column(String(200))
    amount = Column(Float)
    
    cardholder = relationship("Cardholder", back_populates="transactions")

class Statement(Base):
    __tablename__ = 'statements'
    
    id = Column(Integer, primary_key=True)
    cardholder_id = Column(Integer, ForeignKey('cardholders.id'))
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
    
    cardholder = relationship("Cardholder", back_populates="statements")
