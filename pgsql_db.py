import psycopg2
from psycopg2 import sql


def store_report(employee_id, employee_name, summary, status, email_id):
    # Convert status to lowercase to handle case sensitivity
    status = status.lower()

    # Ensure the status is either 'accept' or 'decline'
    if status in ['accept', 'decline']:
        # Connect to PostgreSQL database
        conn = psycopg2.connect(
            dbname="company",
            user="postgres",
            password="surya",
            host="localhost",  # Change this to the correct hostname or IP address
            port="5432"  # Change this to the correct port if needed
        )
        cursor = conn.cursor()

        # Ensure the reports table exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                employee_id INTEGER,
                employee_name TEXT,
                summary TEXT,
                status TEXT,
                email_id TEXT
            )
        ''')

        # Insert the provided information into the reports table
        cursor.execute('''
            INSERT INTO reports (employee_id, employee_name, summary, status, email_id)
            VALUES (%s, %s, %s, %s, %s)
        ''', (employee_id, employee_name, summary, status, email_id))

        conn.commit()
        cursor.close()
        conn.close()

        print(
            f"Report for employee {employee_name} (ID: {employee_id}) with status '{status}' has been stored successfully.")
    else:
        print("Invalid status. Report will not be stored.")
