FROM python:3.14-slim

LABEL io.modelcontextprotocol.server.name="io.github.anselmoo/mcp-zen-of-languages"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends tini \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install .

ENTRYPOINT ["tini", "--"]
CMD ["mcp-zen-of-languages"]
