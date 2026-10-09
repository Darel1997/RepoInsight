FROM python:3.11-slim

WORKDIR /app

# system deps for psycopg2 and building wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Pin PyTorch (pulled in by sentence-transformers) to a version that matches
# transformers 4.46. On ARM servers (e.g. Oracle Ampere) PyPI's build is
# already CPU-only and small (~90 MB).
RUN pip install --no-cache-dir torch==2.5.1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download the local embedding model at build time so the first repo
# analysis doesn't stall on an 80 MB download.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
