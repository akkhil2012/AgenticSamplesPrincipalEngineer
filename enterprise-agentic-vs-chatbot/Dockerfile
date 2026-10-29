# syntax=docker/dockerfile:1
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
COPY data ./data
COPY dashboard ./dashboard
RUN --mount=type=secret,id=proxy_ca \
    if [ -f /run/secrets/proxy_ca ]; then export PIP_CERT=/run/secrets/proxy_ca; fi; \
    pip install --no-cache-dir . && useradd --uid 10001 --create-home demo && mkdir /state && chown demo /state
RUN chmod -R a+rX /app
USER demo
EXPOSE 8000 8501
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
