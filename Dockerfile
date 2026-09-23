FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY scripts/ scripts/
COPY sql/ sql/
COPY tests/ tests/

RUN mkdir -p data work/parquet outputs

CMD ["python", "-m", "scripts.execute_sql"]