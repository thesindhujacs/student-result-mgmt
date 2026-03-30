FROM python:3.11-slim

WORKDIR /app

# Copy backend files
COPY backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \
    --index-url https://pypi.org/simple/ \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org

COPY backend/ .

# Copy frontend into the image
COPY frontend/ ./frontend/

EXPOSE 5000

CMD ["python", "app.py"]