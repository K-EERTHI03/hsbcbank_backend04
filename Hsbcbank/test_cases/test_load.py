from locust import HttpUser, task, between
import json
from datetime import datetime, timedelta

class StatementGenerationUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Sample payload data
        self.payload = {
            "cardholder": {
                "name": "Test User",
                "card_number": "1234567890123456",
                "billing_address": "123 Test St",
                "email": "test@example.com",
                "phone": "1234567890"
            },
            "statement": {
                "statement_date": (datetime.now()).strftime("%Y-%m-%d"),
                "previous_balance": 1000.00,
                "payments_received": 500.00,
                "purchases_charges": 100.00,
                "finance_charges": 10.00,
                "new_balance": 610.00,
                "credit_limit": 5000.00,
                "available_credit": 4390.00,
                "payment_due_date": (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d"),
                "reward_points": 100
            },
            "transactions": [
                {
                    "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                    "description": f"Test Transaction {i}",
                    "amount": 100.00 + i
                } for i in range(10)
            ],
            "language": "en"
        }

    @task(1)
    def generate_statement(self):
        with self.client.post(
            "/api/generate-statement",
            json=self.payload,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                self.environment.runner.transaction_success += 1
                response.success()
            else:
                self.environment.runner.transaction_failure += 1
                response.failure(f"Failed with status {response.status_code}: {response.text}")

    @task(2)
    def preview_statement(self):
        with self.client.post(
            "/preview-statement",
            json=self.payload,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                self.environment.runner.transaction_success += 1
                response.success()
            else:
                self.environment.runner.transaction_failure += 1
                response.failure(f"Failed with status {response.status_code}: {response.text}")