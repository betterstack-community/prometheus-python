FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Enable Flask debug mode
ENV FLASK_DEBUG=1

EXPOSE 8000

CMD ["python", "main.py"]
