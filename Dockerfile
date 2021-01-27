FROM python:3.8.7-slim

COPY requirements.txt /
RUN pip3 install -r requirements.txt

COPY ./app /app

CMD ["gunicorn", "-b 0.0.0.0:4567", "app:app"]