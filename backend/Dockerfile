FROM python:3.10-slim

# Install system dependencies (required for Tesseract OCR, OpenCV, and headless Chrome Selenium)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libtesseract-dev \
    ffmpeg \
    libsm6 \
    libxext6 \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application source
COPY . .

EXPOSE 5000

# Set environment variables for Selenium inside Docker
ENV TESSERACT_PATH=/usr/bin/tesseract
ENV CHROME_DRIVER_PATH=/usr/bin/chromedriver

CMD ["python", "run.py"]
