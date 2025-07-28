FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py ./

# Cloud Run will set PORT environment variable
EXPOSE 8080

CMD ["python", "-u", "maps_to_waze_bot.py"]