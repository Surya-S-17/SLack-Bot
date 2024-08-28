import os
import json
from slack_bolt import App
from slack_sdk import WebClient
from slack_bolt.adapter.socket_mode import SocketModeHandler
from paddleocr import PaddleOCR, draw_ocr
from langchain_community.llms import Ollama
from dotenv import load_dotenv
import psycopg2
import requests  # For image download
from send_expense_report import send_expense_report_of
from email_slack import send_email
from pdf2image import convert_from_path
import numpy as np
import cv2
import spacy
from date_amount import extract_date_and_amount
from slack_sdk.errors import SlackApiError
from pgsql_db import store_report



nlp = spacy.load('categorizer')
# Load environment variables from .env file
load_dotenv('.env')

# Database connection
conn = psycopg2.connect(
    dbname="company",
    user="postgres",
    password="surya",
    host="localhost",  # Change this to the correct hostname or IP address
    port="5432"  # Change this to the correct port if needed
)

cursor = conn.cursor()

# Initialize PaddleOCR
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
paddleocr = PaddleOCR(lang="en", ocr_version="PP-OCRv4", show_log=False, use_gpu=True)
slm = Ollama(model="phi3")



# Initialize Slack app
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Dictionary to store user input data
info_dict = {}


def paddle_scan(paddleocr, img_path_or_nparray):
    try:
        result = paddleocr.ocr(img_path_or_nparray, cls=True)
        result = result[0]
        boxes = [line[0] for line in result]  # bounding box
        txts = [line[1][0] for line in result]  # raw text
        scores = [line[1][1] for line in result]  # scores
        return txts, result
    except Exception as e:
        print("Error in paddle_scan:", e)
        return [], []


def process_image(image_path):
    try:
        image = cv2.imread(image_path)
        return paddle_scan(paddleocr, image)
    except Exception as e:
        print("Error in process_image:", e)
        return [], []


def process_pdf(pdf_path):
    try:
        pages = convert_from_path(pdf_path)
        all_texts = []
        all_results = []

        for page in pages:
            page_array = np.array(page)
            page_texts, page_results = paddle_scan(paddleocr, page_array)
            all_texts.extend(page_texts)
            all_results.extend(page_results)

        return all_texts, all_results
    except Exception as e:
        print("Error in process_pdf:", e)
        return [], []


def process_file(file_path):
    try:
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            return process_image(file_path)
        elif file_path.lower().endswith('.pdf'):
            return process_pdf(file_path)
        else:
            raise ValueError("Unsupported file format. Please provide an image or PDF file.")
    except Exception as e:
        print("Error in process_file:", e)
        return [], []


def extract_info(data):
    try:
        doc = nlp(data)
        max_category = max(doc.cats, key=doc.cats.get)
        max_score = doc.cats[max_category]

        print(max_category)

        return max_category
    except Exception as e:
        print("Error in extract_info:", e)
        return None


def ex(file_path):
    try:
        receipt_texts, receipt_boxes = process_file(file_path)
        ex_text = " ".join(receipt_texts)
        ress=extract_date_and_amount(ex_text)
        date=ress[0]
        amount=ress[1]
        expense_type = extract_info(ex_text)
        return [expense_type,date,amount]
    except Exception as e:
        print("Error in ex:", e)
        return None


def extract_text(data):
    greeting = ['hi', 'hello', 'mrng', 'heyy']
    bye = ['bye', 'thanks', 'ok']
    if data.get('subtype') == 'file_share':
        try:
            file_info = data.get('files', [])[0] if 'files' in data else None
            if file_info:
                # Access file information
                file_id = file_info["id"]
                file_name = file_info["name"]
                file_type = file_info["filetype"]

                # Download and store based on file type (modify logic for PDF handling)
                if file_type in ["jpg", "jpeg", "png", "pdf"]:  # Add supported image/pdf extensions
                    ress = download_and_store_file(file_id, file_name)
                    expense_type = ress[0][0]
                    date = ress[0][1]
                    amount = ress[0][2]
                    image_path = ress[1]
                    name = info_dict.get("user_name", "Unknown")
                    employee_id = info_dict.get("employee_id", "Unknown")
                    
                    send_expense_report_of(expense_type, name, employee_id, date, amount, image_path)
                    txt = f"*Expense Report :rocket:*\nSubmitted by: {name}\nID: {employee_id}\nExpense Category: {expense_type}\nAmount: {amount}\nDate: {date}"
                    info_dict['summary']=txt
                    # send_email(id, card)
                    blocks = [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": txt
                            }
                        }
                    ]
                    return "Expense Report", blocks
                else:
                    return f"Unsupported file type: {file_type}. Please upload an image or PDF.", None
            else:
                return "No file information found.", None
        except Exception as e:
            print("Error in extract_text (file_share):", e)
            return "Error processing file.", None
    elif data.get('type') == 'message':
        try:
            if data['text'].lower() in greeting:
                return "Enter your employee ID",None
            elif data['text'].lower() in bye:
                return "Thank you.\nI will notify you once manager reviewed your request",None
            else:
                # Assuming user responds with their employee ID
                employee_id = data["text"]
                info_dict["employee_id"] = employee_id

                # Query local database to get user's name
                cursor.execute("SELECT name, email_id FROM employees WHERE employee_id = %s", (employee_id,))
                result = cursor.fetchone()
                if result:
                    user_name, email_id = result
                    info_dict["user_name"] = user_name
                    info_dict["email_id"] = email_id
                    return f"Hello, {user_name}! Please upload your image or receipt (pdf).",None
                else:
                    return "Sorry, I couldn't find your name.",None


        except Exception as e:
            print("Error in extract_text (message):", e)
            return "Error processing message.",None
    return "Unsupported message type.",None



def download_and_store_file(file_id, file_name):
    try:
        headers = {
            "Authorization": f"Bearer {os.environ.get('SLACK_BOT_TOKEN')}"
        }
        download_url = f"https://slack.com/api/files.info?file={file_id}"
        response = requests.get(download_url, headers=headers)
        file_info = response.json()

        if file_info.get("ok"):
            file_url = file_info["file"]["url_private_download"]
            file_response = requests.get(file_url, headers=headers)
            file_data = file_response.content

            # Create a folder (if needed) and store the file
            folder_path = "uploads"  # Replace with your desired folder name
            os.makedirs(folder_path, exist_ok=True)  # Create folder if it doesn't exist
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, "wb") as f:
                f.write(file_data)

            print(f"File downloaded and saved to: {file_path}")
            return [ex(file_path),file_path]
        else:
            print(f"Failed to get file information: {file_info.get('error')}")
            return None, None
    except Exception as e:
        print("Error in download_and_store_file:", e)
        return None, None


@app.event("message")
def message_handler(event, say):
    text = event.get('text', '')
    print(f"Message text: {event}")

    output, blocks = extract_text(event)  # Pass the event object for processing
    if blocks is not None:
        say(blocks=blocks, text=output)
    else:
        say(output)

@app.action("accept_action")
def handle_accept(ack, body, say):
    ack()
    user_id = body["user"]["id"]
    say(f"Thank you <@{user_id}>! The expense report has been accepted.")
    final_response("accept")

@app.action("decline_action")
def handle_decline(ack, body, say):
    ack()
    user_id = body["user"]["id"]
    say(f"Thank you <@{user_id}>! The expense report has been declined.")
    final_response("decline")

@app.action("view_receipt_action")
def handle_view_receipt(ack, body, client, say):
    ack()
    image_path = body["actions"][0]["value"]
    channel_id = body["channel"]["id"]

    try:
        response = client.files_upload(
            channels=channel_id,
            file=image_path,
            initial_comment="Here is the receipt:"
        )

        blocks =[
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Accept"
                                },
                                "style": "primary",
                                "action_id": "accept_action"
                            },
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Decline"
                                },
                                "style": "danger",
                                "action_id": "decline_action"
                            }
                        ]
                    }
                ]

        client.chat_postMessage(
            channel=channel_id,
            text="Please review the receipt and choose an option:",
            blocks=blocks
        )
    except SlackApiError as e:
        print(f"Error uploading file: {e.response['error']}")

def final_response(action):
    store_report(info_dict["employee_id"], info_dict["user_name"],info_dict["summary"], action,info_dict["email_id"])
    name=info_dict["user_name"]
    card=f"Hi {name},\n\n \tyour expense is reviewed and {action}ed by the manager "
    send_email(info_dict["email_id"], card)
    print(f"Final response received: {action}")

if __name__ == "__main__":

    # Start the Bolt app
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])  # Use SLACK_APP_TOKEN here
    handler.start()


