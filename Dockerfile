FROM python:3.11-slim 
 
WORKDIR /app 
 
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt 

RUN echo "Cache invalidated 1"
 
COPY . . 

# Make sure both the database file and its parent directory are writable
RUN chmod 777 /app && \
    chmod 666 /app/disputes.db && \
    # Ensure the database file is owned by the user running the application
    chown 1000:1000 /app/disputes.db || true

# Create a non-root user to run the application
RUN useradd -m appuser
USER appuser
 
ENV PYTHONPATH=/app 
 
CMD ["python", "app/entrypoint.py"]