# syntax=docker/dockerfile:1.4

FROM python:3.14.3-alpine3.23
# Font
COPY --link config/schoolboek.woff /usr/local/share/fonts/schoolboek.woff
RUN apk add --no-cache fontconfig cairo && fc-cache -f
# Cache dependencies
COPY --link requirements.txt ./server/
RUN pip install --no-cache-dir -r server/requirements.txt
# Copy source
COPY --link . ./server
CMD ["fastapi", "run", "server/app.py"]
