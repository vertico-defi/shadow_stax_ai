FROM python:3.11-slim

WORKDIR /app
COPY apps/chatbot/backend/requirements.txt /app/apps/chatbot/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/apps/chatbot/backend/requirements.txt

ENV PYTHONPATH=/app
