import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

client = WebClient(token=SLACK_BOT_TOKEN)

def send_message(text: str, channel_id: str):

    client.chat_postMessage(channel=channel_id, text=text)
    print(f"Message sent to channel {channel_id}")