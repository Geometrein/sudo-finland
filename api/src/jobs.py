import os
import logging
import requests

import asyncio
import telegram
from telegram.constants import ParseMode
from dotenv import load_dotenv

load_dotenv()

# logging
LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(level=logging.INFO, format=LOGGING_FORMAT, datefmt=DATE_FORMAT)
logger = logging.getLogger(__name__)

# Get telegram Vars
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
BOT = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# Get jobs API Vars
JOBS_API_PROVIDER = os.getenv('JOBS_API_PROVIDER')
JOBS_API_KEY = os.getenv('JOBS_API_KEY')
JOBS_API_HOST = os.getenv('JOBS_API_HOST')
JOBS_API_URL = os.getenv('JOBS_API_URL')


def get_job_listings(item):
    headers = {
        f'x-{JOBS_API_PROVIDER}-key': JOBS_API_KEY,
        f'x-{JOBS_API_PROVIDER}-host': JOBS_API_HOST
    }
    params = {
        "keywords": item.keyword,
        "locationId": item.location_id,  # Helsinki Metropolitan Area
        "datePosted": item.date_posted,
        "sort": "mostRelevant"
    }

    response = requests.get(JOBS_API_URL, headers=headers, params=params)
    response_details = {
        "status_code": response.status_code,
        "headers": response.headers,
        "content": response.content,
        "text": response.text,
        "json": response.json()
    }
    logger.info(response_details)
    if response.status_code == 200:
        return response
    else:
        response.raise_for_status()


def preprocess_listings(response_object, top_k=10):
    response_dict = response_object.json()
    messages = "Today's job listings:\n\n"

    for listing_dict in response_dict['data'][:top_k]:
        job_title = listing_dict['title']
        url = listing_dict['url']
        company_name = listing_dict["company"]["name"]
        post_date = listing_dict["postDate"]
        message = (
            f"<b>Company:</b> {company_name}\n"
            f"<b>Job Title:</b> {job_title}\n"
            f"<b>Link:</b> <a href='{url}'>Job Link</a>\n\n"
        )
        messages += message
    messages += f"<b>\nTags:</b> #job, #itjobsfinland, #itjobs"
    return messages


async def send_to_telegram(message_text):
    try:
        logger.info(f"Sending the message to: {CHANNEL_ID}")
        await BOT.send_message(
            chat_id=CHANNEL_ID,
            text=message_text,
            parse_mode=ParseMode.HTML
        )
        logger.info(f"Message sent to: {CHANNEL_ID}")
    except Exception as error:
        logger.error(f"Failed to send the message {error}")


async def jobs_main(item):
    jobs_api_response = get_job_listings(item)
    messages = preprocess_listings(response_object=jobs_api_response)
    logger.info(f"Sending {len(messages)} listings as messages.")
    await send_to_telegram(messages)
