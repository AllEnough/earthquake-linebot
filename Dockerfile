# 使用 Python 3.11 以避免 pmdarima 相容性問題
FROM python:3.11-slim

# 安裝系統層級相依套件（含建構工具、gfortran、libatlas for pmdarima）
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gfortran \
    libatlas-base-dev \
    liblapack-dev \
    libblas-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /app

# 複製程式碼與需求檔案
COPY . .

# 安裝 Python 套件（包含 numpy, pmdarima）
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 開啟服務用的 port（Railway 預設使用 PORT 環境變數）
ENV PORT=8080
EXPOSE 8080

# 啟動 Flask 應用
CMD ["python", "main.py"]
