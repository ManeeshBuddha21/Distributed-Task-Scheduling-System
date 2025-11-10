FROM python:3.11-slim

WORKDIR /app
COPY ../api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Create runtime dirs
RUN mkdir -p /app/queue /app/completed
VOLUME ["/app/queue", "/app/completed"]

COPY ../api /app/api
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]
