import logging

from fastapi import FastAPI, Depends, HTTPException

from src.auth import token_validation
from src.events import meetup_main

# logging
LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(level=logging.INFO, format=LOGGING_FORMAT, datefmt=DATE_FORMAT)
logger = logging.getLogger(__name__)


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "-Luke, I am your API. -Noooo.", "status_code": 200}


@app.get("/publish-events/", dependencies=[Depends(token_validation)])
async def publish_events():
    try:
        await meetup_main()
        return {"message": "Successfully published events.", "status_code": 200}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Encountered an Unexpected error: {e}"
        )
