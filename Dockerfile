FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=src/app.py
ENV FLASK_ENV=production

EXPOSE 80

CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "4", "--access-logfile", "-", "wsgi:app"]
