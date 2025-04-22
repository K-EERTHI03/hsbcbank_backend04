import os
import logging
import gc
from flask import Flask, request, jsonify, render_template, send_file, session
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Cardholder, Transaction, Statement
from pdf_generator import StatementPDFGenerator
from languages import LANGUAGE_PACKS, LANGUAGE_CODES
from performance_logger import PerformanceLogger
import datetime
import tempfile
import uuid

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
if not app.secret_key:
    raise ValueError("SESSION_SECRET environment variable is required")
CORS(app)

# Database connection
DATABASE_URI = os.environ.get('DATABASE_URL')
if DATABASE_URI is None:
    # Fallback to SQLite for local development
    DATABASE_URI = 'sqlite:///credit_card.db'
    logger.warning("No DATABASE_URL found, using SQLite instead")

# For PostgreSQL from SQLAlchemy 1.4.x
if DATABASE_URI.startswith("postgres://"):
    DATABASE_URI = DATABASE_URI.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URI)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

perf_logger = PerformanceLogger()

@app.route('/')
def index():
    """Render the main page"""
    languages = [(code, lang['name']) for code, lang in LANGUAGE_PACKS.items()]
    return render_template('index.html', languages=languages, LANGUAGE_PACKS=LANGUAGE_PACKS)

@app.route('/api/generate-statement', methods=['POST'])
def generate_statement():
    """Generate a credit card statement PDF based on user input"""
    try:
        perf_logger.start('generate_statement')
        
        # Extract request data
        data = request.json
        language = data.get('language', 'en')
        
        # Validate language
        if language not in LANGUAGE_CODES:
            return jsonify({'error': LANGUAGE_PACKS[language].get('invalid_language', 'Invalid language code')}), 400
        
        # Extract cardholder data
        name = data.get('name')
        card_number = data.get('card_number')
        email = data.get('email')
        phone = data.get('phone')
        
        # Get error messages in the selected language
        error_messages = {
            'missing_fields': LANGUAGE_PACKS[language].get('missing_fields', 'Missing required fields'),
            'invalid_email': LANGUAGE_PACKS[language].get('invalid_email', 'Invalid email address'),
            'invalid_card': LANGUAGE_PACKS[language].get('invalid_card', 'Invalid card number'),
            'invalid_phone': LANGUAGE_PACKS[language].get('invalid_phone', 'Invalid phone number')
        }
        
        # Validate required fields
        if not all([name, card_number, email, phone]):
            return jsonify({'error': error_messages['missing_fields']}), 400
            
        # Basic validation for email, card number and phone (could be enhanced)
        if '@' not in email:
            return jsonify({'error': error_messages['invalid_email']}), 400
        
        # Create database session
        db_session = Session()
        
        try:
            # Create cardholder
            perf_logger.start('create_cardholder')
            cardholder = Cardholder(
                name=name,
                card_number=card_number,
                billing_address=data.get('billing_address', "D-45, Green Park,\nNew Delhi-110016, India"),
                email=email,
                phone=phone
            )
            db_session.add(cardholder)
            db_session.commit()
            perf_logger.end('create_cardholder')
            
            # Create transactions with batch processing for large datasets
            perf_logger.start('create_transactions')
            
            # Process input transactions
            transaction_data = data.get('transactions', [])
            transactions = []
            
            # Define batch size for DB operations
            batch_size = 50
            total_transactions = len(transaction_data)
            
            # Log the number of transactions
            if total_transactions > 20:
                logger.info(f"Processing large transaction set: {total_transactions} transactions")
            
            # Process transactions in batches to handle large datasets efficiently
            for i in range(0, total_transactions, batch_size):
                batch = transaction_data[i:i+batch_size]
                batch_transactions = []
                
                for tx_data in batch:
                    # Parse date with fallback
                    try:
                        tx_date = datetime.datetime.strptime(tx_data.get('date', '2025-03-02'), '%Y-%m-%d').date()
                    except ValueError:
                        # Fallback to current date if format is invalid
                        tx_date = datetime.date.today()
                        
                    # Create transaction object
                    transaction = Transaction(
                        cardholder_id=cardholder.id,
                        date=tx_date,
                        description=tx_data.get('description', 'Transaction'),
                        amount=float(tx_data.get('amount', 0))
                    )
                    batch_transactions.append(transaction)
                
                # Add batch to DB and commit
                if batch_transactions:
                    db_session.add_all(batch_transactions)
                    db_session.commit()
                    transactions.extend(batch_transactions)
                
                # Force garbage collection after each batch
                batch_transactions = None
                gc.collect()
            
            # Add some default transactions if none provided
            if not transactions:
                logger.debug("No transactions provided, adding default sample transactions")
                default_transactions = [
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
                    ),
                    Transaction(
                        cardholder_id=cardholder.id,
                        date=datetime.date(2025, 3, 3),
                        description="Big Bazaar - Grocery",
                        amount=1230.75
                    ),
                    Transaction(
                        cardholder_id=cardholder.id,
                        date=datetime.date(2025, 3, 5),
                        description="Mobile Recharge",
                        amount=499.00
                    )
                ]
                db_session.add_all(default_transactions)
                db_session.commit()
                transactions.extend(default_transactions)
            
            perf_logger.end('create_transactions')
            
            # Create statement
            perf_logger.start('create_statement')
            statement = Statement(
                cardholder_id=cardholder.id,
                statement_date=datetime.date.today(),
                previous_balance=data.get('previous_balance', 13840.00),
                payments_received=data.get('payments_received', 175.50),
                purchases_charges=data.get('purchases_charges', 640.00),
                finance_charges=data.get('finance_charges', 45.00),
                new_balance=data.get('new_balance', 13935.50),
                credit_limit=data.get('credit_limit', 175.00),
                available_credit=data.get('available_credit', 1230.00),
                payment_due_date=datetime.date.today() + datetime.timedelta(days=21),
                reward_points=data.get('reward_points', 175)
            )
            db_session.add(statement)
            db_session.commit()
            perf_logger.end('create_statement')
            
            # Generate PDF
            perf_logger.start('pdf_generation')
            
            # Create a temporary file with a unique name
            unique_id = str(uuid.uuid4())
            temp_dir = tempfile.mkdtemp()
            output_path = os.path.join(temp_dir, f'credit_card_statement_{unique_id}.pdf')
            
            pdf_generator = StatementPDFGenerator(
                statement, 
                cardholder, 
                transactions, 
                language
            )
            pdf_generator.generate_pdf(output_path)
            perf_logger.end('pdf_generation')
            
            # Store the generated PDF path in session for later retrieval
            session['generated_pdf'] = output_path
            
            performance_data = perf_logger.get_metrics()
            perf_logger.end('generate_statement')
            
            return jsonify({
                'success': True, 
                'message': 'Statement generated successfully',
                'performance': performance_data,
                'download_url': f'/download-statement/{unique_id}'
            })
            
        except Exception as e:
            logger.error(f"Error generating statement: {str(e)}")
            db_session.rollback()
            return jsonify({'error': str(e)}), 500
        finally:
            db_session.close()
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download-statement/<string:unique_id>')
def download_statement(unique_id):
    """Download the generated PDF statement"""
    pdf_path = session.get('generated_pdf')
    
    if not pdf_path or not os.path.exists(pdf_path):
        return jsonify({'error': 'PDF not found or expired'}), 404
    
    return send_file(
        pdf_path,
        as_attachment=True,
        download_name=f'credit_card_statement_{unique_id}.pdf',
        mimetype='application/pdf'
    )

@app.route('/api/languages')
def get_languages():
    """Return the list of supported languages"""
    languages = {code: {'name': lang['name']} for code, lang in LANGUAGE_PACKS.items()}
    return jsonify(languages)

@app.route('/preview-statement', methods=['POST'])
def preview_statement():
    """Generate a preview of the statement data"""
    try:
        data = request.json
        language = data.get('language', 'en')
        
        # Validate language
        if language not in LANGUAGE_CODES:
            return jsonify({'error': 'Invalid language code'}), 400
        
        language_pack = LANGUAGE_PACKS[language]
        
        # Build statement data for preview
        statement_data = {
            'cardholder': {
                'name': data.get('name', 'Sample Name'),
                'card_number': data.get('card_number', 'XXXX-XXXX-XXXX-1234'),
                'billing_address': data.get('billing_address', 'Sample Address'),
                'email': data.get('email', 'sample@example.com'),
                'phone': data.get('phone', '1234567890')
            },
            'statement': {
                'statement_date': datetime.date.today().strftime('%d-%b-%Y'),
                'previous_balance': data.get('previous_balance', 13840.00),
                'payments_received': data.get('payments_received', 175.50),
                'purchases_charges': data.get('purchases_charges', 640.00),
                'finance_charges': data.get('finance_charges', 45.00),
                'new_balance': data.get('new_balance', 13935.50),
                'credit_limit': data.get('credit_limit', 175.00),
                'available_credit': data.get('available_credit', 1230.00),
                'payment_due_date': (datetime.date.today() + datetime.timedelta(days=21)).strftime('%d-%b-%Y'),
                'reward_points': data.get('reward_points', 175)
            },
            'transactions': data.get('transactions', [
                {
                    'date': '02-Mar-2025',
                    'description': 'Amazon India - Electronics',
                    'amount': 3499.00
                },
                {
                    'date': '02-Mar-2025',
                    'description': 'Uber Ride - New Delhi',
                    'amount': 285.50
                }
            ]),
            'language': language_pack
        }
        
        return render_template('statement.html', **statement_data)
        
    except Exception as e:
        logger.error(f"Error generating preview: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
