FROM python:3.10

# 必要なビルドツールとライブラリをインストール
RUN apt-get update && \
    apt-get install -y build-essential gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /bot
COPY requirements.txt /bot/
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . /bot
CMD ["python", "main.py"]
