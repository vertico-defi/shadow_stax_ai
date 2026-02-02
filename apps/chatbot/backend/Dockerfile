FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends sqlite3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY apps/chatbot/backend/requirements.txt /app/apps/chatbot/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/apps/chatbot/backend/requirements.txt

ENV PYTHONPATH=/app
