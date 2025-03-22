FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod 666 /app/disputes.db

 
ENV PYTHONPATH=/app 

CMD ["python", "app/entrypoint.py"]
