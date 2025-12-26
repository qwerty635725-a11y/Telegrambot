FROM python:3.11-slim

# Устанавливаем нужные языки
RUN apt-get update && apt-get install -y \
    g++ \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
