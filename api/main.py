import logging
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.events import meetup_main
from src.jobs import jobs_main

# logging
LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
logging.basicConfig(level=logging.INFO, format=LOGGING_FORMAT, datefmt=DATE_FORMAT)
logger = logging.getLogger(__name__)


app = FastAPI()


class EventItem(BaseModel):
    token: str


class JobItem(BaseModel):
    token: str
    keyword: str
    location_id: int
    date_posted: str


@app.get("/")
async def root():
    return {"message": "-Luke, I am your API. -Noooo.", "status_code": 200}


@app.post("/publish-events/")
async def publish_events(item: EventItem):
    try:
        if item.token == AUTH_TOKEN:
            await meetup_main()
            return {"message": "Successfully published events.", "status_code": 200}
        else:
            raise HTTPException(status_code=403,  detail="You shall not pass!")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Encountered an Unexpected error: {e}"
        )


@app.post("/publish-jobs/")
async def publish_job_listings(item: JobItem):
    try:
        if item.token == AUTH_TOKEN:
            await jobs_main(item)
            return {"message": "Successfully published jobs.", "status_code": 200}
        else:
            raise HTTPException(status_code=403,  detail="You shall not pass!")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Encountered an Unexpected error: {e}"
        )
