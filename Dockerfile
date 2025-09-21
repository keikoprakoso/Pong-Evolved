FROM python:3.9-slim

WORKDIR /app

COPY python/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000 5001

CMD ["python", "python/inference_server.py"]