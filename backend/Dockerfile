FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /workspace

COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m pip install --upgrade pip && pip install .

COPY backend/pyproject.toml ./backend/pyproject.toml
COPY backend/reusable_data_fetcher.py ./backend/reusable_data_fetcher.py
COPY backend/app ./backend/app
COPY backend/alembic ./backend/alembic
COPY backend/alembic.ini ./backend/alembic.ini
RUN pip install ./backend && python -c "import reusable_data_fetcher" \
    && addgroup --system sahmi \
    && adduser --system --ingroup sahmi --home /home/sahmi sahmi \
    && chown -R sahmi:sahmi /workspace /home/sahmi

WORKDIR /workspace/backend
USER sahmi

EXPOSE 8080

CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
