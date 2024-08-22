# Fase de build
FROM python:3.11-slim AS build

RUN apt-get update && apt-get install -y --no-install-recommends build-essential zlib1g

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Fase final
FROM python:3.11-slim

WORKDIR /app

COPY --from=build /app /app

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
