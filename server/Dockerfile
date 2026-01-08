# syntax=docker/dockerfile:1.4

FROM python:3.14.2-alpine3.23
# Cache dependencies
COPY --link requirements.txt ./server/
RUN pip install --no-cache-dir -r server/requirements.txt && apk add cairo
# Copy source
COPY --link . ./server
CMD ["fastapi", "run", "server/app.py"]
