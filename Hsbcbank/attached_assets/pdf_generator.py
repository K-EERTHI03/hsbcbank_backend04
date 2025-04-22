from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import datetime

class StatementPDFGenerator:
    def __init__(self, statement, cardholder, transactions):
        self.statement = statement
        self.cardholder = cardholder
        self.transactions = transactions
        
    def generate_pdf(self, output_path):
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Add Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30
        )
        elements.append(Paragraph("Credit Card Statement", title_style))
        
        # Cardholder Information
        cardholder_data = [
            ["Cardholder Information", ""],
            ["Name:", self.cardholder.name],
            ["Card Number:", "XXXX-XXXX-XXXX-" + self.cardholder.card_number[-4:]],
            ["Billing Address:", self.cardholder.billing_address],
            ["Email:", self.cardholder.email],
            ["Phone:", self.cardholder.phone]
        ]
        
        cardholder_table = Table(cardholder_data, colWidths=[2*inch, 4*inch])
        cardholder_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(cardholder_table)
        elements.append(Spacer(1, 20))
        
        # Statement Summary
        summary_data = [
            ["Statement Summary", "Amount (INR)"],
            ["Previous Balance:", f"₹ {self.statement.previous_balance:,.2f}"],
            ["Payments Received:", f"₹ {self.statement.payments_received:,.2f}"],
            ["Purchases & Charges:", f"₹ {self.statement.purchases_charges:,.2f}"],
            ["Finance Charges:", f"₹ {self.statement.finance_charges:,.2f}"],
            ["New Balance:", f"₹ {self.statement.new_balance:,.2f}"],
            ["Credit Limit:", f"₹ {self.statement.credit_limit:,.2f}"],
            ["Available Credit:", f"₹ {self.statement.available_credit:,.2f}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 20))
        
        # Transactions
        transaction_data = [["Date", "Description", "Amount (INR)"]]
        for trans in self.transactions:
            transaction_data.append([
                trans.date.strftime("%d-%b-%y"),
                trans.description,
                f"₹ {trans.amount:,.2f}"
            ])
        
        transaction_table = Table(transaction_data, colWidths=[1.5*inch, 4*inch, 1.5*inch])
        transaction_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(transaction_table)
        
        doc.build(elements)