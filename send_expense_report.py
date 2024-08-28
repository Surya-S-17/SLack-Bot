import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('.env')

# Initialize Slack client and Bolt app
client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
app1 = App(token=os.environ["SLACK_BOT_TOKEN"], signing_secret=os.environ["SLACK_SIGNING_SECRET"])

def send_expense_report_of(expense_category, user_name, employee_id, date, amount, image_path):
    channel_id = "C06V0HCN36Z"

    # Define the blocks for the expense report message
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Expense Report :rocket:*\nSubmitted by: {user_name}\nID: {employee_id}\nExpense Category: {expense_category}\nAmount: {amount}\nDate: {date}"
            }
        },
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
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View Receipt"
                    },
                    "action_id": "view_receipt_action",
                    "value": image_path
                }
            ]
        }
    ]

    try:
        response = client.chat_postMessage(
            channel=channel_id,
            text="Expense Report",
            blocks=blocks
        )
        print(f"Expense report sent to channel {channel_id}")
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")

@app1.action("accept_action")
def handle_accept(ack, body, say):
    ack()
    user_id = body["user"]["id"]
    say(f"Thank you <@{user_id}>! The expense report has been accepted.")
    final_response("accept")

@app1.action("decline_action")
def handle_decline(ack, body, say):
    ack()
    user_id = body["user"]["id"]
    say(f"Thank you <@{user_id}>! The expense report has been declined.")
    final_response("decline")

@app1.action("view_receipt_action")
def handle_view_receipt(ack, body, client, say):
    ack()
    image_path = body["actions"][0]["value"]
    channel_id = body["channel"]["id"]

    # Send the receipt image
    try:
        response = client.files_upload(
            channels=channel_id,
            file=image_path,
            initial_comment="Here is the receipt:"
        )

        # Send the follow-up message with accept/decline buttons
        blocks = [
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
    print(f"Final response received: {action}")

if __name__ == "__main__":
    send_expense_report_of("Travel", "John Doe", "12345", "2024-06-08", "$500", "Safari.pdf")
    
    # Start the Bolt app
    handler = SocketModeHandler(app1, os.environ["SLACK_APP_TOKEN"])  # Use SLACK_APP_TOKEN here
    handler.start()

