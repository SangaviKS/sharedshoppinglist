FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN sed '/^:::/d' requirements.txt > requirements.clean.txt && pip install --no-cache-dir -r requirements.clean.txt
COPY . .
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
