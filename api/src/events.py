import os
import time
import logging
from datetime import datetime, timedelta
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

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
BOT = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

FEED_URL = 'https://www.meetup.com/gql2'

HEADERS = {
    'accept': '*/*',
    'accept-language': 'en-US',
    'apollographql-client-name': 'nextjs-web',
    'content-type': 'application/json',
    'cookie': '',
    'dnt': '1',
    'origin': 'https://www.meetup.com',
    'priority': 'u=1, i',
    'referer': 'https://www.meetup.com/find/?source=EVENTS&sortField=DATETIME&location=fi--Helsinki&categoryId=546&distance=twentyFiveMiles&dateRange=next-week',
    'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36',
    'x-meetup-view-id': 'c3c36fa0-85ae-4ea2-a603-0583b2fc1a17'
}


def generate_dynamic_payload() -> dict:
    logger.info('Generating dynamic payload...')
    today = datetime.now()
    same_weekday_next_week = today + timedelta(days=7)
    next_weekday_next_week = today + timedelta(days=8)
    start_date_range = same_weekday_next_week.strftime("%Y-%m-%dT17:00:00-04:00")
    end_date_range = next_weekday_next_week.strftime("%Y-%m-%dT16:59:59-04:00")

    payload = {
        "operationName": "recommendedEventsWithSeries",
        "variables": {
            "first": 20,
            "lat": "60.16999816894531",  # Helsinki Coords
            "lon": "24.940000534057617",  # Helsinki Coords
            "topicCategoryId": "546",  # Technology
            "radius": 25,  # Radius in miles from coords above
            "startDateRange": start_date_range,  # search time window start
            "endDateRange": end_date_range,  # search time window end
            "numberOfEventsForSeries": 5,
            "seriesStartDate": today.strftime("%Y-%m-%d"),  # Today
            "sortField": "DATETIME",
            "doConsolidateEvents": True,
            "doPromotePaypalEvents": True,
            "indexAlias": "popular_events_nearby_current"
        },
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "415d07768f1183a2a33a4eeb477f7269e547a28735d3dccffad73a0c1b878c92"
            }
        }
    }
    return payload


def convert_time(date_time_str: str) -> str:
    logger.info('Generating dynamic payload...')
    date_time_obj = datetime.fromisoformat(date_time_str)
    readable_date_time = date_time_obj.strftime('%A, %B %d, %Y %I:%M %p %Z')
    return readable_date_time


async def send_single_message(text: str) -> None:
    try:
        logger.info(f"Sending the message to: {CHANNEL_ID}")
        await BOT.send_message(
            chat_id=CHANNEL_ID,
            text=text,
            parse_mode=ParseMode.HTML,
            message_thread_id=282
        )
        logger.info(f"Message sent to: {CHANNEL_ID}")
    except Exception as error:
        logger.error(f"Failed to send the message {error}")


async def fetch_events(url: str, headers: dict, payload: dict) -> list:
    logger.info('fetching events...')
    try:
        response = requests.post(url, headers=headers, json=payload)
        logger.info(f'Status code: {response.status_code}')
        response.raise_for_status()
        data = response.json()
        return data['data']['result']['edges']
    except requests.RequestException as error:
        logger.error(f"HTTP Request failed: {error}")
        return []


async def meetup_main() -> None:
    payload = generate_dynamic_payload()
    events = await fetch_events(FEED_URL, HEADERS, payload)
    logger.info(f'Found {len(events)} events.')
    for event in events:
        node = event['node']
        title = node['title']
        date_time = convert_time(date_time_str=node['dateTime'])
        event_url = node['eventUrl']
        group_name = node['group']['name']
        message = (
            f"<b>Event:</b> {title}\n\n"
            f"<b>Date and Time:</b> {date_time}\n\n"
            f"<b>Group:</b> {group_name}\n\n"
            f"<b>URL:</b> <a href='{event_url}'>Event Link</a>\n\n"
            f"<b>Tags:</b> #events"
        )
        await send_single_message(message)
        logger.info(f'Event sent to group.')
        time.sleep(2)


if __name__ == "__main__":
    asyncio.run(meetup_main())
