from simple_salesforce import Salesforce
from faker import Faker
import random
import os
from datetime import date
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()


# initialize Faker
fake = Faker()

# Salesforce credentials
SF_USERNAME = os.getenv('SF_USERNAME')
SF_PASSWORD = os.getenv('SF_PASSWORD')
SF_SECURITY_TOKEN = os.getenv('SF_SECURITY_TOKEN')
SF_CLIENT_ID = os.getenv('SF_CLIENT_ID')
SF_CLIENT_SECRET = os.getenv('SF_CLIENT_SECRET')
SF_URL = os.getenv('SF_URL')
TEST_USER_IDS = os.getenv('TEST_USER_IDS').split(',')
print("SF_USERNAME: ", SF_USERNAME)
print(f"TEST_USER_IDS: ", TEST_USER_IDS)

# Connect to Salesforce
sf = Salesforce(
    username=SF_USERNAME,
    password=SF_PASSWORD,
    security_token=SF_SECURITY_TOKEN,
    domain='login'
)

def create_account(owner_id):
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
        "OwnerId": owner_id,  # Use the passed owner_id
    }
    return sf.Account.create(account)

def create_contact(account_id, owner_id):
    contact = {
        "FirstName": fake.first_name(),
        "LastName": fake.last_name(),
        "Email": fake.email(),
        "Phone": fake.phone_number(),
        "AccountId": account_id,
        "OwnerId": owner_id,  # Use the passed owner_id
    }
    return sf.Contact.create(contact)

def create_lead(owner_id):
    lead = {
        "FirstName": fake.first_name(),
        "LastName": fake.last_name(),
        "Company": fake.company(),
        "Email": fake.email(),
        "Phone": fake.phone_number(),
        "Status": random.choice(["New", "Working", "Closed - Not Converted"]),
        "OwnerId": owner_id,  # Use the passed owner_id
    }
    return sf.Lead.create(lead)


def create_opportunity(account_id, owner_id):
    opportunity = {
        "Name": f"{fake.company()} - {date.today().strftime('%Y-%m-%d')}",
        "AccountId": account_id,
        "CloseDate": fake.date_between(start_date='today', end_date='+30d').strftime('%Y-%m-%d'),
        "StageName": random.choice(["Qualifying", "Active", "Proposal/Price Quote", "Ready to Close", "Closed Won", "Closed Lost"]),
        "Amount": random.randint(1000, 200000),
        "OwnerId": owner_id,  # Use the passed owner_id
    }
    return sf.Opportunity.create(opportunity)

CALL_SUBJECTS = [
    "Call with client",
    "Follow-up call",
    "Discussion about project",
    "Client feedback call",
    "Call to negotiate terms",
    "Introduction call",
    "Call to discuss quote",
    "Check-in call",
    "Call to update on progress",
    "Call to resolve issues",
]

TASK_SUBJECTS = [
    "Send quote",
    "Prepare contract",
    "Schedule meeting",
    "Conduct research",
    "Draft email to client",
    "Update project plan",
    "Review contract terms",
    "Create presentation",
    "Send reminder for meeting",
    "Follow up on action items",
]

def create_task(contact_id, task_type, owner_id):
    if task_type == "Call":
        subject = random.choice(CALL_SUBJECTS)
        status = "Completed"  # Calls are typically logged as completed
        activity_date = fake.date_between(start_date='-1y', end_date='today').strftime('%Y-%m-%d')  # Past date for completed tasks
        task = {
            "Subject": subject,
            "Status": status,
            "WhoId": contact_id,
            "OwnerId": owner_id,  # Use the passed owner_id
            "ActivityDate": activity_date,
            "TaskSubtype": "Call",  # Specify TaskSubtype as Call
        }
    else:  # Task
        subject = random.choice(TASK_SUBJECTS)
        status = random.choice(["Not Started", "In Progress", "Completed"])
        # Set ActivityDate based on the task's status
        if status == "Completed":
            activity_date = fake.date_between(start_date='-1y', end_date='today').strftime('%Y-%m-%d')  # Past date
        else:
            activity_date = fake.date_between(start_date='today', end_date='+30d').strftime('%Y-%m-%d')  # Future date
        task = {
            "Subject": subject,
            "Status": status,
            "WhoId": contact_id,
            "OwnerId": owner_id,  # Use the passed owner_id
            "ActivityDate": activity_date,
            "TaskSubtype": "Task",  # Specify TaskSubtype as Task
        }
    return sf.Task.create(task)

def generate_test_data(num_accounts=0, contacts_per_account=0, opps_per_account=0, num_leads=0, num_tasks=0):
    print("Generating test data...")
    owner_index = 0  # Initialize owner index

    for _ in range(num_accounts):
        # Alternate owner for account
        owner_id = TEST_USER_IDS[owner_index % len(TEST_USER_IDS)]
        account_result = create_account(owner_id)
        owner_index += 1  # Increment owner index
        if account_result['success']:
            account_id = account_result['id']
            print(f"Created Account: {account_id}")

            # Create contacts
            for _ in range(contacts_per_account):
                contact_result = create_contact(account_id, owner_id)  # Use the same owner_id as the account
                if contact_result['success']:
                    contact_id = contact_result['id']
                    print(f"Created Contact: {contact_result['id']}")

                    # Alternate between creating a call and a task
                    for i in range(num_tasks):
                        task_type = "Call" if i % 2 == 0 else "Task"
                        task_result = create_task(contact_id, task_type, owner_id)  # Use the same owner_id as the account
                        if task_result['success']:
                            print(f"Created {task_type}: {task_result['id']}")

            # Create opportunities
            for _ in range(opps_per_account):
                opp_result = create_opportunity(account_id, owner_id)  # Use the same owner_id as the account
                if opp_result['success']:
                    print(f"Created Opportunity: {opp_result['id']}")

    # Create leads
    for _ in range(num_leads):
        # Alternate owner for lead
        owner_id = TEST_USER_IDS[owner_index % len(TEST_USER_IDS)]
        lead_result = create_lead(owner_id)
        owner_index += 1  # Increment owner index
        if lead_result['success']:
            print(f"Created Lead: {lead_result['id']}")

if __name__ == "__main__":
    try:
        generate_test_data(
            num_accounts=5,
            contacts_per_account=2,
            opps_per_account=1,
            num_leads=2,
            num_tasks=3
        )
        print("Test data generation completed successfully.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")