# Events Worker
This worker sends meetup.com events to the telegram channel.

## Local Run
Create .env file with
`TELEGRAM_BOT_TOKEN` and `CHANNEL_ID`

Run:
```
docker build --no-cache -t sudo_finland_api_image .
docker run --rm -it -d --name sudo_finland_api_container -p 80:80 sudo_finland_api_image
```