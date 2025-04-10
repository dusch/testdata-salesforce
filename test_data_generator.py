from simple_salesforce import Salesforce
from faker import Faker
import random
import os
from datetime import date
import random


# initialize Faker
fake = Faker()

# Salesforce credentials
SF_USERNAME = os.getenv('SF_USERNAME')
SF_PASSWORD = os.getenv('SF_PASSWORD')
SF_SECURITY_TOKEN = os.getenv('SF_SECURITY_TOKEN')
SF_CLIENT_ID = os.getenv('SF_CLIENT_ID')
SF_CLIENT_SECRET = os.getenv('SF_CLIENT_SECRET')
SF_URL = os.getenv('SF_URL')

# Connect to Salesforce
sf = Salesforce(
    username=SF_USERNAME,
    password=SF_PASSWORD,
    security_token=SF_SECURITY_TOKEN,
    domain='login'
)

def create_account():
    account = {
        "Name": fake.company(),
        "Phone": fake.phone_number(),
        "Industry": random.choice(["Technology", "Finance", "Healthcare", "Food & Beverage"]),
        "Website": fake.url(),
        "BillingStreet": fake.street_address(),
        "BillingCity": fake.city(),
        "BillingState": fake.state(),
        "BillingPostalCode": fake.zipcode(),
        "BillingCountry": 'United States',
    }
    return sf.Account.create(account)

def create_contact(account_id):
    contact = {
        "FirstName": fake.first_name(),
        "LastName": fake.last_name(),
        "Email": fake.email(),
        "Phone": fake.phone_number(),
        "AccountId": account_id,
    }
    return sf.Contact.create(contact)


def create_opportunity(account_id):
    opportunity = {
        "Name": f"{fake.company()} - {date.today().strftime('%Y-%m-%d')}",
        "AccountId": account_id,
        "CloseDate": fake.date_between(start_date='today', end_date='+30d').strftime('%Y-%m-%d'),
        "StageName": random.choice(["Prospecting", "Qualification", "Needs Analysis", "Value Proposition", "Negotiation/Review"]),
        "Amount": random.randint(1000, 100000),
    }
    return sf.Opportunity.create(opportunity)

def generate_test_data(num_accounts=5, contacts_per_account=2, opps_per_account=1):
    print("Generating test data...")
    for _ in range(num_accounts):
       # Create account
       account_result = create_account()
       if account_result['success']:
        account_id = account_result['id']
        print(f"Created Account: {account_id}")

        # Create contacts
        for _ in range(contacts_per_account):
            contact_result = create_contact(account_id)
            if contact_result['success']:
                print(f"Created Contact: {contact_result['id']}")
        
        # Create opportunities
        for _ in range(opps_per_account):
            opp_result = create_opportunity(account_id)
            if opp_result['success']:
                print(f"Created Opportunity: {opp_result['id']}")

if __name__ == "__main__":
    try:
        generate_test_data(
            num_accounts=5,
            contacts_per_account=2,
            opps_per_account=1
        )
        print("Test data generation completed successfully.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")