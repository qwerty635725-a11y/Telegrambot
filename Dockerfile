FROM python:3.11-slim

# Создаём непривилегированного пользователя
RUN useradd -m sandbox

# Устанавливаем нужные языки
RUN apt-get update && apt-get install -y \
    g++ \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Запуск НЕ от root
USER sandbox

CMD ["python", "main.py"]
