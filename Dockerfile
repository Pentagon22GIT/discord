# ベースイメージ
FROM python:3.11

# 作業ディレクトリを設定
WORKDIR /bot

# 必要なシステムパッケージをインストール
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libzbar0

# Python依存関係をインストール
COPY requirements.txt /bot/
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . /bot

# アプリケーションを実行
CMD ["python", "main.py"]
