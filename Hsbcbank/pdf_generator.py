import logging
import gc
import psutil
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from languages import LANGUAGE_PACKS
import datetime
import os
import tempfile
from performance_logger import PerformanceLogger

logger = logging.getLogger(__name__)
perf_logger = PerformanceLogger()

# Register fonts for multilingual support
try:
    # Define font paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    font_dir = os.path.join(base_dir, 'static', 'fonts')

    # Register Noto Sans fonts for multilingual support
    pdfmetrics.registerFont(TTFont('NotoSans', os.path.join(font_dir, 'NotoSans-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('NotoSansBold', os.path.join(font_dir, 'NotoSans-Bold.ttf')))
    pdfmetrics.registerFont(TTFont('NotoSansTamil', os.path.join(font_dir, 'NotoSansTamil-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('NotoSansTamilBold', os.path.join(font_dir, 'NotoSansTamil-Bold.ttf')))
    pdfmetrics.registerFont(TTFont('NotoSansDevanagari', os.path.join(font_dir, 'NotoSansDevanagari-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('NotoSansDevangariBold', os.path.join(font_dir, 'NotoSansDevanagari-Bold.ttf')))

    # Create font family groupings for better text rendering
    # English font family
    pdfmetrics.registerFontFamily(
        'NotoSans', 
        normal='NotoSans', 
        bold='NotoSansBold'
    )

    # Tamil font family - important for proper rendering
    pdfmetrics.registerFontFamily(
        'NotoSansTamil', 
        normal='NotoSansTamil', 
        bold='NotoSansTamilBold'
    )

    # Hindi font family
    pdfmetrics.registerFontFamily(
        'NotoSansDevanagari', 
        normal='NotoSansDevanagari', 
        bold='NotoSansDevangariBold'
    )

    logger.info("Successfully registered custom fonts with language-specific families")
except Exception as e:
    logger.warning(f"Could not register custom fonts: {str(e)}")
    logger.warning("Falling back to built-in fonts")

class StatementPDFGenerator:
    def __init__(self, statement, cardholder, transactions, language='en'):
        self.statement = statement
        self.cardholder = cardholder
        self.transactions = transactions
        self.language = language
        self.lang_pack = LANGUAGE_PACKS.get(language, LANGUAGE_PACKS['en'])
        self.page_size = A4
        self.batch_size = 20  # Maximum number of transactions per page
        self.max_memory_usage = 100  # Maximum memory usage in MB
        self.optimize_for_large_dataset = len(transactions) > 20  # Automatically optimize for large datasets
        self.hsbc_red = colors.Color(red=0.8, green=0.1, blue=0.1) #added hsbc red color


    def get_font_for_language(self, is_bold=False):
        """Return the appropriate font name for the selected language"""
        if self.language == 'en':
            return 'NotoSansBold' if is_bold else 'NotoSans'
        elif self.language == 'ta':
            # For Tamil, we need to be explicit about font selection
            return 'NotoSansTamilBold' if is_bold else 'NotoSansTamil'
        elif self.language == 'hi':
            return 'NotoSansDevangariBold' if is_bold else 'NotoSansDevanagari'
        return 'NotoSansBold' if is_bold else 'NotoSans'

    def create_text_object(self, text, style):
        """Create a properly rendered text object with the correct font for the language"""
        # Apply special text handling for Tamil language
        if self.language == 'ta':
            # Ensure text is properly encoded
            if isinstance(text, str):
                # Use the Tamil font explicitly for this text
                style.fontName = self.get_font_for_language(is_bold='Bold' in style.fontName)
                # For complex scripts like Tamil, we need to add special handling
                style.encoding = 'utf-8'  # Ensure proper Unicode encoding
                style.wordWrap = 'CJK'  # Use CJK word wrapping for better complex script support
                style.allowWidows = 0
                style.allowOrphans = 0
                style.language = 'Tamil'
        elif self.language == 'hi':
            # For Hindi text
            if isinstance(text, str):
                style.fontName = self.get_font_for_language(is_bold='Bold' in style.fontName)
                style.encoding = 'utf-8'
                style.wordWrap = 'CJK'
                style.language = 'Hindi'

        # Create the paragraph with proper font configuration
        return Paragraph(text, style)

    def generate_pdf(self, output_path):
        """Generate the credit card statement PDF with the selected language"""
        perf_logger.start('pdf_generation_total')

        # Create a temporary file for building the PDF
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_path = temp_file.name
        temp_file.close()

        try:
            doc = SimpleDocTemplate(temp_path, pagesize=self.page_size)
            styles = getSampleStyleSheet()
            elements = []

            # Add title
            perf_logger.start('title_section')
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontName=self.get_font_for_language(is_bold=True),
                fontSize=16,
                spaceAfter=30,
                textColor=self.hsbc_red,
                alignment=1  # Center alignment
            )
            elements.append(self.create_text_object(self.lang_pack['title'], title_style))
            perf_logger.end('title_section')

            # Cardholder Information
            perf_logger.start('cardholder_section')

            # For Tamil language, we need special paragraph handling for tabular data
            if self.language == 'ta':
                # Create styles for the table cells
                header_style = ParagraphStyle(
                    'TableHeader',
                    fontName=self.get_font_for_language(is_bold=True),
                    fontSize=14,
                    alignment=0,  # Left alignment
                    wordWrap='CJK',
                    encoding='utf-8',
                    language='Tamil'
                )
                label_style = ParagraphStyle(
                    'TableLabel',
                    fontName=self.get_font_for_language(is_bold=True),
                    fontSize=10,
                    alignment=0,  # Left alignment
                    wordWrap='CJK',
                    encoding='utf-8',
                    language='Tamil'
                )
                value_style = ParagraphStyle(
                    'TableValue',
                    fontName=self.get_font_for_language(),
                    fontSize=10,
                    alignment=0,  # Left alignment
                    wordWrap='CJK',
                    encoding='utf-8',
                    language='Tamil'
                )

                # Create paragraph objects for each table cell to ensure correct Tamil rendering
                cardholder_data = [
                    [self.create_text_object(self.lang_pack['cardholder_info'], header_style), ""],
                    [self.create_text_object(self.lang_pack['name'], label_style), 
                     self.create_text_object(self.cardholder.name, value_style)],
                    [self.create_text_object(self.lang_pack['card_number'], label_style), 
                     self.create_text_object("XXXX-XXXX-XXXX-" + self.cardholder.card_number[-4:], value_style)],
                    [self.create_text_object(self.lang_pack['billing_address'], label_style), 
                     self.create_text_object(self.cardholder.billing_address, value_style)],
                    [self.create_text_object(self.lang_pack['email'], label_style), 
                     self.create_text_object(self.cardholder.email, value_style)],
                    [self.create_text_object(self.lang_pack['phone'], label_style), 
                     self.create_text_object(self.cardholder.phone, value_style)]
                ]
            else:
                # For other languages, use the standard approach
                cardholder_data = [
                    [self.lang_pack['cardholder_info'], ""],
                    [self.lang_pack['name'], self.cardholder.name],
                    [self.lang_pack['card_number'], "XXXX-XXXX-XXXX-" + self.cardholder.card_number[-4:]],
                    [self.lang_pack['billing_address'], self.cardholder.billing_address],
                    [self.lang_pack['email'], self.cardholder.email],
                    [self.lang_pack['phone'], self.cardholder.phone]
                ]

            cardholder_table = Table(cardholder_data, colWidths=[2.5*inch, 4*inch])
            cardholder_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.hsbc_red), #Updated
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white), #Updated
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), self.get_font_for_language(is_bold=True)),
                ('FONTNAME', (0, 1), (0, -1), self.get_font_for_language(is_bold=True)),
                ('FONTNAME', (1, 1), (1, -1), self.get_font_for_language()),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('FONTSIZE', (0, 1), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            elements.append(cardholder_table)
            elements.append(Spacer(1, 20))
            perf_logger.end('cardholder_section')

            # Statement Summary
            perf_logger.start('summary_section')
            currency_symbol = self.lang_pack.get('currency_symbol', '₹')

            # For Tamil language, we need special paragraph handling for tabular data
            if self.language == 'ta':
                # Create styles for the table cells
                header_style = ParagraphStyle(
                    'SummaryHeader',
                    fontName=self.get_font_for_language(is_bold=True),
                    fontSize=14,
                    alignment=0,  # Left alignment
                    wordWrap='CJK',
                    encoding='utf-8',
                    language='Tamil'
                )
                label_style = ParagraphStyle(
                    'SummaryLabel',
                    fontName=self.get_font_for_language(is_bold=True),
                    fontSize=10,
                    alignment=0,  # Left alignment
                    wordWrap='CJK',
                    encoding='utf-8',
                    language='Tamil'
                )
                value_style = ParagraphStyle(
                    'SummaryValue',
                    fontName=self.get_font_for_language(),
                    fontSize=10,
                    alignment=0,  # Left alignment
                    wordWrap='CJK',
                    encoding='utf-8',
                    language='Tamil'
                )

                # Create paragraph objects for each table cell to ensure correct Tamil rendering
                summary_data = [
                    [
                        self.create_text_object(self.lang_pack['statement_summary'], header_style),
                        self.create_text_object(self.lang_pack['amount'], header_style)
                    ],
                    [
                        self.create_text_object(self.lang_pack['previous_balance'], label_style),
                        self.create_text_object(f"{currency_symbol} {self.statement.previous_balance:,.2f}", value_style)
                    ],
                    [
                        self.create_text_object(self.lang_pack['payments_received'], label_style),
                        self.create_text_object(f"{currency_symbol} {self.statement.payments_received:,.2f}", value_style)
                    ],
                    [
                        self.create_text_object(self.lang_pack['purchases_charges'], label_style),
                        self.create_text_object(f"{currency_symbol} {self.statement.purchases_charges:,.2f}", value_style)
                    ],
                    [
                        self.create_text_object(self.lang_pack['finance_charges'], label_style),
                        self.create_text_object(f"{currency_symbol} {self.statement.finance_charges:,.2f}", value_style)
                    ],
                    [
                        self.create_text_object(self.lang_pack['new_balance'], label_style),
                        self.create_text_object(f"{currency_symbol} {self.statement.new_balance:,.2f}", value_style)
                    ],
                    [
                        self.create_text_object(self.lang_pack['credit_limit'], label_style),
                        self.create_text_object(f"{currency_symbol} {self.statement.credit_limit:,.2f}", value_style)
                    ],
                    [
                        self.create_text_object(self.lang_pack['available_credit'], label_style),
                        self.create_text_object(f"{currency_symbol} {self.statement.available_credit:,.2f}", value_style)
                    ]
                ]
            else:
                # For other languages, use the standard approach
                summary_data = [
                    [self.lang_pack['statement_summary'], self.lang_pack['amount']],
                    [self.lang_pack['previous_balance'], f"{currency_symbol} {self.statement.previous_balance:,.2f}"],
                    [self.lang_pack['payments_received'], f"{currency_symbol} {self.statement.payments_received:,.2f}"],
                    [self.lang_pack['purchases_charges'], f"{currency_symbol} {self.statement.purchases_charges:,.2f}"],
                    [self.lang_pack['finance_charges'], f"{currency_symbol} {self.statement.finance_charges:,.2f}"],
                    [self.lang_pack['new_balance'], f"{currency_symbol} {self.statement.new_balance:,.2f}"],
                    [self.lang_pack['credit_limit'], f"{currency_symbol} {self.statement.credit_limit:,.2f}"],
                    [self.lang_pack['available_credit'], f"{currency_symbol} {self.statement.available_credit:,.2f}"]
                ]

            summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.hsbc_red), #Updated
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white), #Updated
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), self.get_font_for_language(is_bold=True)),
                ('FONTNAME', (0, 1), (0, -1), self.get_font_for_language(is_bold=True)),
                ('FONTNAME', (1, 1), (1, -1), self.get_font_for_language()),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(summary_table)
            elements.append(Spacer(1, 20))
            perf_logger.end('summary_section')

            # Transactions - implemented with batching for large datasets
            perf_logger.start('transactions_section')

            # Add transaction header
            transaction_header = self.create_text_object(self.lang_pack['transactions'], title_style)
            elements.append(transaction_header)
            elements.append(Spacer(1, 10))

            # Process transactions in batches with optimizations for large datasets
            total_transactions = len(self.transactions)

            # Determine optimal batch size based on total transactions
            if self.optimize_for_large_dataset:
                logger.info(f"Optimizing PDF generation for large dataset ({total_transactions} transactions)")
                # For very large datasets, reduce batch size to manage memory better
                if total_transactions > 100:
                    self.batch_size = 15
                elif total_transactions > 50:
                    self.batch_size = 18

            batch_count = (total_transactions + self.batch_size - 1) // self.batch_size
            logger.debug(f"Processing {total_transactions} transactions in {batch_count} batches of {self.batch_size}")

            # Reusable style for transaction tables
            transaction_table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.hsbc_red), #Updated
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white), #Updated
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), self.get_font_for_language(is_bold=True)),
                ('FONTNAME', (0, 1), (-1, -1), self.get_font_for_language()),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ])

            # Column headers - create once and reuse
            transaction_headers = [
                self.lang_pack['date'], 
                self.lang_pack['description'], 
                self.lang_pack['amount']
            ]

            # Process each batch
            for batch_index in range(batch_count):
                perf_logger.start(f'transaction_batch_{batch_index}')

                start_idx = batch_index * self.batch_size
                end_idx = min(start_idx + self.batch_size, total_transactions)

                # Get only the transactions for this batch to minimize memory usage
                batch_transactions = self.transactions[start_idx:end_idx]

                # Create transaction table for this batch
                # For Tamil language, we need to create custom Paragraph objects for each cell
                if self.language == 'ta':
                    # For Tamil language, wrap each header in a properly styled paragraph
                    header_style = ParagraphStyle(
                        'TableHeader',
                        fontName=self.get_font_for_language(is_bold=True),
                        fontSize=12,
                        alignment=0,  # Left alignment
                        wordWrap='CJK',
                        encoding='utf-8',
                        language='Tamil'
                    )
                    cell_style = ParagraphStyle(
                        'TableCell',
                        fontName=self.get_font_for_language(),
                        fontSize=10,
                        alignment=0,  # Left alignment
                        wordWrap='CJK',
                        encoding='utf-8',
                        language='Tamil'
                    )

                    # Create paragraphs for each header
                    header_row = [
                        self.create_text_object(self.lang_pack['date'], header_style),
                        self.create_text_object(self.lang_pack['description'], header_style),
                        self.create_text_object(self.lang_pack['amount'], header_style)
                    ]

                    # Start with our custom header row
                    transaction_data = [header_row]

                    # Build the transaction data rows with custom text objects
                    for trans in batch_transactions:
                        # Format date according to language
                        date_str = trans.date.strftime("%d-%b-%y")

                        # Format amount according to language with currency symbol
                        amount_str = f"{currency_symbol} {trans.amount:,.2f}"

                        # Create a row with text objects for each cell
                        transaction_data.append([
                            self.create_text_object(date_str, cell_style),
                            self.create_text_object(trans.description, cell_style),
                            self.create_text_object(amount_str, cell_style)
                        ])
                else:
                    # For other languages, use the standard approach
                    transaction_data = [transaction_headers]

                    # Build the transaction data rows normally
                    for trans in batch_transactions:
                        # Format date according to language
                        date_str = trans.date.strftime("%d-%b-%y")

                        # Format amount according to language with currency symbol
                        amount_str = f"{currency_symbol} {trans.amount:,.2f}"

                        transaction_data.append([
                            date_str,
                            trans.description,
                            amount_str
                        ])

                # Create table with appropriate column widths
                transaction_table = Table(
                    transaction_data, 
                    colWidths=[1.5*inch, 4*inch, 1.5*inch],
                    repeatRows=1
                )
                transaction_table.setStyle(transaction_table_style)

                # Add table to document elements
                elements.append(transaction_table)

                # Add batch number and page information for large datasets
                if self.optimize_for_large_dataset and batch_count > 1:
                    page_info_style = ParagraphStyle(
                        'PageInfo',
                        parent=styles['Normal'],
                        fontName=self.get_font_for_language(),
                        fontSize=8,
                        alignment=1,  # Center alignment
                        spaceAfter=10
                    )
                    page_text = f"{self.lang_pack['page']} {batch_index + 1} {self.lang_pack['of']} {batch_count}"
                    elements.append(self.create_text_object(page_text, page_info_style))

                # Add a page break between batches, except for the last batch
                if batch_index < batch_count - 1:
                    elements.append(PageBreak())

                # Memory optimization - clear local variables and force garbage collection
                batch_transactions = None
                transaction_data = None
                transaction_table = None
                gc.collect()

                # Monitor memory usage and log warning if approaching threshold
                current_memory = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)  # Convert to MB
                if current_memory > self.max_memory_usage:
                    logger.warning(f"Memory usage high during PDF generation: {current_memory:.2f} MB")

                perf_logger.end(f'transaction_batch_{batch_index}')

            perf_logger.end('transactions_section')

            # Add footer with statement disclaimer and page numbers
            perf_logger.start('footer_section')

            # Create a function to add page numbers and footer to each page
            def add_page_footer(canvas, doc):
                canvas.saveState()
                # Draw footer text
                footer_text = self.lang_pack.get('statement_footer', 'Thank you for your business.')
                footer_style = ParagraphStyle(
                    'Footer',
                    parent=styles['Normal'],
                    fontName=self.get_font_for_language(),
                    fontSize=8,
                    alignment=1,  # Center alignment
                )
                # Create a text object with the footer text
                p = self.create_text_object(footer_text, footer_style)
                # Set the position for the footer (at the bottom of the page)
                w, h = p.wrap(doc.width, doc.bottomMargin)
                p.drawOn(canvas, doc.leftMargin, 0.5 * inch)

                # Add page number
                page_num_text = f"{self.lang_pack.get('page', 'Page')} {doc.page} {self.lang_pack.get('of', 'of')} {doc.page}"
                canvas.setFont(self.get_font_for_language(), 9)
                canvas.drawRightString(doc.pagesize[0] - 0.5 * inch, 0.5 * inch, page_num_text)

                # Add statement date at the bottom left
                date_str = self.statement.statement_date.strftime("%d-%b-%Y")
                date_text = f"{self.lang_pack.get('statement_date', 'Statement Date')}: {date_str}"
                canvas.setFont(self.get_font_for_language(), 9)
                canvas.drawString(doc.leftMargin, 0.75 * inch, date_text)

                canvas.restoreState()

            perf_logger.end('footer_section')

            # Build the document with the page footer function
            perf_logger.start('build_document')
            doc.build(elements, onFirstPage=add_page_footer, onLaterPages=add_page_footer)
            perf_logger.end('build_document')

            # Copy the temporary file to the final output path
            perf_logger.start('copy_to_output')
            with open(temp_path, 'rb') as src_file:
                with open(output_path, 'wb') as dst_file:
                    dst_file.write(src_file.read())
            perf_logger.end('copy_to_output')

        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

            perf_logger.end('pdf_generation_total')

            # Log performance metrics
            performance_data = perf_logger.get_metrics()
            logger.debug(f"PDF Generation Performance: {performance_data}")