import os

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

from src.log import Logger

load_dotenv()

logger = Logger().get_logger()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

client = WebClient(token=SLACK_BOT_TOKEN)

def send_message(text: str, channel_id: str):
    try:
        client.chat_postMessage(channel=channel_id, text=text)
        logger.info(f"Menssagem {text} enviada para o canal: {channel_id}")
    except SlackApiError as e:
        logger.error(f"Erro ao enviar mensagem para o Slack: {e.response['error']}")

def send_blocks(blocks: list, channel_id: str, text_fallback: str = "Atualização de fluxo"):
    try:
        client.chat_postMessage(channel=channel_id, text=text_fallback, blocks=blocks)
    except SlackApiError as e:
        logger.error(f"Erro ao enviar para Slack: {e.response['error']}")