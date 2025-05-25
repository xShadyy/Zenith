FROM python:3.13.2-alpine

LABEL org.opencontainers.image.title="zenith" \
      org.opencontainers.image.description="Flexible Framework for Conducting Penetration Tests" \
      org.opencontainers.image.author="xShadyy" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/xShadyy/zenith" \
      org.opencontainers.image.documentation="https://zenith.dev/"

# Environment variables for efficient builds
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

COPY . /zenith
WORKDIR /zenith

RUN apk add --update --no-cache git nmap nmap-scripts && pip install -e .

CMD ["--info"]
ENTRYPOINT ["zenith"]
