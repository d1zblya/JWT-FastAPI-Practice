FROM python:3.12-slim

WORKDIR /app
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src /app/src
COPY prestart.sh /app/prestart.sh
COPY alembic.ini /app/alembic.ini

RUN chmod +x /app/prestart.sh

EXPOSE 8000

ENTRYPOINT ["/app/prestart.sh"]