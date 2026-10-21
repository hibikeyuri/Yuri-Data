FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY modern/requirements.txt /tmp/requirements.txt
RUN python -m pip install --no-cache-dir -r /tmp/requirements.txt \
    && groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid 10001 --home-dir /app app
COPY modern /app/modern
USER 10001:10001
EXPOSE 8000
CMD ["gunicorn", "--workers", "1", "--threads", "2", "--bind", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-", "modern.app:app"]
