FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir "psycopg[binary]"

COPY app2.py .

EXPOSE 9000

CMD ["python3", "app2.py"]
