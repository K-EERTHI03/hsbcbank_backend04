
# Credit Card Statement System Validation Rules

## Input Field Validations

### Card Number
- Must be exactly 16 digits
- Numeric only (no hyphens or spaces)
- Example: 1234567890123456

### Cardholder Name
- Length: 2-40 characters
- Only letters and spaces allowed
- Example: John Smith

### ZIP Code
- Must be 5 or 6 digits
- Numeric only
- Examples: 12345, 123456

### Date Format
- Must be YYYY-MM-DD
- Must be a valid calendar date
- Example: 2025-03-15

### Transaction Amount
- Must be positive number
- Up to 2 decimal places allowed
- Example: 123.45

### Currency
- Must be one of: INR, USD, GBP, EUR
- Example: INR

### Email ID
- Must contain @ symbol
- Must have valid domain
- Example: user@example.com

### CVV
- Exactly 3 digits
- Numeric only
- Example: 123

### Expiry Date
- Format: MM/YY
- Must not be a past date
- Example: 12/25

### Language
- Supported codes: en (English), ta (Tamil), hi (Hindi)
- Default: en
