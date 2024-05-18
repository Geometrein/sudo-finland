# Events Worker
This worker sends meetup.com events to the telegramc channel.

## Local Run
Create .env file with
`TELEGRAM_BOT_TOKEN` and `CHANNEL_ID`

Run:
```
docker build --no-cache -t events_worker_image .
docker run --rm -it -d --name events_worker_container -p 80:80 events_worker_image
```