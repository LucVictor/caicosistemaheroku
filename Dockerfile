FROM python:3.9

WORKDIR /app

# Copia só o requirements.txt primeiro para aproveitar cache do docker
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Agora copia todo o restante do código
COPY . .

CMD ["gunicorn", "wsgi:app", "--bind", "0.0.0.0:8000"]
