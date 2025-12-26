FROM mcr.microsoft.com/dotnet/sdk:7.0

RUN apt-get update && apt-get install -y \
    python3 python3-pip g++ nodejs npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python3", "main.py"]
