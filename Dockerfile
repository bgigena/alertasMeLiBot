FROM python:3.11-slim

# Evitar que Python escriba archivos .pyc y forzar logs sin buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos solo el script
COPY botMeLiAlertas.py .

CMD ["python", "botMeLiAlertas.py"]
