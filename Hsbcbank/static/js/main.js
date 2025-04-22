document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners to language tabs
    const langTabs = document.querySelectorAll('[data-bs-toggle="tab"]');
    langTabs.forEach(tab => {
        tab.addEventListener('shown.bs.tab', function (event) {
            const language = event.target.getAttribute('data-language');
            console.log(`Switched to language: ${language}`);
            updateTranslations(language);
        });
    });

    // Initialize with default language (English)
    updateTranslations('en');

    // Add event listeners to "Add Transaction" buttons
    const addTransactionBtns = document.querySelectorAll('.add-transaction-btn');
    addTransactionBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const language = this.getAttribute('data-language');
            addTransactionRow(language);
        });
    });

    // Add event listeners to "Generate Statement" buttons (form submission)
    const statementForms = document.querySelectorAll('.statement-form');
    statementForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const language = this.getAttribute('data-language');
            generateStatement(language);
        });
    });

    // Add event listeners to "Preview" buttons
    const previewBtns = document.querySelectorAll('.preview-btn');
    previewBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const language = this.getAttribute('data-language');
            previewStatement(language);
        });
    });
});

// Function to add a new transaction row
function addTransactionRow(language) {
    const container = document.getElementById(`transaction-container-${language}`);
    
    // Create a new transaction item
    const transactionItem = document.createElement('div');
    transactionItem.className = 'transaction-item mb-3';
    
    // Get today's date in YYYY-MM-DD format
    const today = new Date();
    const formattedDate = today.toISOString().split('T')[0];
    
    // Get translations for the current language
    const translations = window.TRANSLATIONS && window.TRANSLATIONS[language] ? window.TRANSLATIONS[language] : {};
    const dateLabel = translations['date'] || 'Date';
    const descriptionLabel = translations['description'] || 'Description';
    const amountLabel = translations['amount'] || 'Amount';
    const removeLabel = translations['remove'] || 'Remove';
    
    transactionItem.innerHTML = `
        <div class="row">
            <div class="col-md-3">
                <label class="form-label" data-translate="date">${dateLabel}</label>
                <input type="date" class="form-control transaction-date" name="transaction_date" value="${formattedDate}">
            </div>
            <div class="col-md-6">
                <label class="form-label" data-translate="description">${descriptionLabel}</label>
                <input type="text" class="form-control transaction-description" name="transaction_description" value="">
            </div>
            <div class="col-md-3">
                <label class="form-label" data-translate="amount">${amountLabel}</label>
                <input type="number" class="form-control transaction-amount" name="transaction_amount" value="0" step="0.01">
            </div>
        </div>
        <button type="button" class="btn btn-sm btn-danger mt-2 remove-transaction-btn" data-translate="remove">${removeLabel}</button>
    `;
    
    // Add event listener to the remove button
    const removeBtn = transactionItem.querySelector('.remove-transaction-btn');
    removeBtn.addEventListener('click', function() {
        transactionItem.remove();
    });
    
    // Append the new transaction item to the container
    container.appendChild(transactionItem);
}

// Function to collect form data for generating statement
function collectFormData(language) {
    const form = document.getElementById(`statementForm-${language}`);
    
    // Collect basic form data
    const formData = {
        name: document.getElementById(`name-${language}`).value,
        card_number: document.getElementById(`card_number-${language}`).value,
        email: document.getElementById(`email-${language}`).value,
        phone: document.getElementById(`phone-${language}`).value,
        billing_address: document.getElementById(`billing_address-${language}`).value,
        previous_balance: parseFloat(document.getElementById(`previous_balance-${language}`).value),
        payments_received: parseFloat(document.getElementById(`payments_received-${language}`).value),
        purchases_charges: parseFloat(document.getElementById(`purchases_charges-${language}`).value),
        finance_charges: parseFloat(document.getElementById(`finance_charges-${language}`).value),
        new_balance: parseFloat(document.getElementById(`new_balance-${language}`).value),
        credit_limit: parseFloat(document.getElementById(`credit_limit-${language}`).value),
        available_credit: parseFloat(document.getElementById(`available_credit-${language}`).value),
        reward_points: parseInt(document.getElementById(`reward_points-${language}`).value),
        language: language,
        transactions: []
    };
    
    // Collect transaction data
    const transactionContainer = document.getElementById(`transaction-container-${language}`);
    const transactionItems = transactionContainer.querySelectorAll('.transaction-item');
    
    transactionItems.forEach(item => {
        const dateInput = item.querySelector('.transaction-date');
        const descriptionInput = item.querySelector('.transaction-description');
        const amountInput = item.querySelector('.transaction-amount');
        
        if (dateInput && descriptionInput && amountInput) {
            formData.transactions.push({
                date: dateInput.value,
                description: descriptionInput.value,
                amount: parseFloat(amountInput.value)
            });
        }
    });
    
    return formData;
}

// Function to generate statement
function generateStatement(language) {
    const formData = collectFormData(language);
    
    // Show loading state
    const generateBtn = document.querySelector(`.generate-btn[data-language="${language}"]`);
    const originalBtnText = generateBtn.innerHTML;
    generateBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating...';
    generateBtn.disabled = true;
    
    // Send AJAX request to generate statement
    fetch('/api/generate-statement', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        // Display performance metrics
        const resultCard = document.getElementById('resultCard');
        resultCard.classList.remove('d-none');
        
        const metricsTableBody = document.getElementById('metrics-table-body');
        metricsTableBody.innerHTML = '';
        
        for (const [operation, metrics] of Object.entries(data.performance)) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${operation}</td>
                <td>${metrics.duration_ms}</td>
                <td>${metrics.memory_change_mb}</td>
            `;
            metricsTableBody.appendChild(row);
        }
        
        // Set download link
        const downloadLink = document.getElementById('downloadLink');
        downloadLink.href = data.download_url;
        
        // Scroll to result card
        resultCard.scrollIntoView({ behavior: 'smooth' });
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while generating the statement. Please try again.');
    })
    .finally(() => {
        // Restore button state
        generateBtn.innerHTML = originalBtnText;
        generateBtn.disabled = false;
    });
}

// Function to update all UI elements with the selected language
function updateTranslations(language) {
    // If no translations available, return
    if (!window.TRANSLATIONS || !window.TRANSLATIONS[language]) {
        console.error(`No translations found for language: ${language}`);
        return;
    }
    
    // Get translations for the selected language
    const translations = window.TRANSLATIONS[language];
    
    // Find all elements with data-translate attribute
    const elements = document.querySelectorAll('[data-translate]');
    
    // Update text content based on translation key
    elements.forEach(element => {
        const key = element.getAttribute('data-translate');
        if (translations[key]) {
            element.textContent = translations[key];
        }
    });
    
    // Also update input placeholders if needed
    const inputElements = document.querySelectorAll('input[data-translate-placeholder]');
    inputElements.forEach(input => {
        const key = input.getAttribute('data-translate-placeholder');
        if (translations[key]) {
            input.placeholder = translations[key];
        }
    });
    
    // Update dynamic transaction row labels for the active tab
    const activeTab = document.querySelector('.tab-pane.active');
    if (activeTab) {
        const labels = activeTab.querySelectorAll('.transaction-item label');
        labels.forEach(label => {
            if (label.textContent === 'Date' && translations['date']) {
                label.textContent = translations['date'];
            } else if (label.textContent === 'Description' && translations['description']) {
                label.textContent = translations['description'];
            } else if (label.textContent === 'Amount' && translations['amount']) {
                label.textContent = translations['amount'];
            }
        });
    }
}

// Function to preview statement
function previewStatement(language) {
    const formData = collectFormData(language);
    
    // Show loading state
    const previewBtn = document.querySelector(`.preview-btn[data-language="${language}"]`);
    const originalBtnText = previewBtn.innerHTML;
    previewBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
    previewBtn.disabled = true;
    
    // Send AJAX request to preview statement
    fetch('/preview-statement', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.text())
    .then(html => {
        // Show the preview in modal
        const previewContent = document.getElementById('previewContent');
        previewContent.innerHTML = html;
        
        // Show modal
        const previewModal = new bootstrap.Modal(document.getElementById('previewModal'));
        previewModal.show();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while generating the preview. Please try again.');
    })
    .finally(() => {
        // Restore button state
        previewBtn.innerHTML = originalBtnText;
        previewBtn.disabled = false;
    });
}
