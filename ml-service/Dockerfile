FROM python:3.14-slim
WORKDIR /app
COPY ml-service/requirements.txt ./ml-service/requirements.txt
RUN pip install --no-cache-dir -r ml-service/requirements.txt
COPY ml-service/ ./ml-service/
COPY models/ ./models/
WORKDIR /app/ml-service
EXPOSE 9999
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9999"]