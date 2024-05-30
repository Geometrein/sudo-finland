FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip3 install --no-cache-dir -r ./requirements.txt

EXPOSE 80

CMD ["gunicorn", "main:app", "--worker-class", "uvicorn.workers.UvicornWorker", "--workers", "4", "-b", "0.0.0.0:80", "--timeout", "240"]