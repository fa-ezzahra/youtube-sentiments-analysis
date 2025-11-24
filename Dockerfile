FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY models/ ./models/
COPY app_api.py .

EXPOSE 7860

CMD ["uvicorn", "app_api:app", "--host", "0.0.0.0", "--port", "7860"]
