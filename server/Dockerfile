# syntax=docker/dockerfile:1

FROM python:3.15.0a8-alpine3.23
# Font
COPY --link config/schoolboek.woff /usr/local/share/fonts/schoolboek.woff
RUN --mount=type=cache,target=/var/cache/apk \
    ln -s /var/cache/apk /etc/apk/cache && \
    apk add fontconfig cairo && fc-cache -f
# Cache dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    pip install -r requirements.txt
# Copy source
COPY --link . ./server
CMD ["fastapi", "run", "server/app.py"]
