FROM python:3.14.2-alpine3.23
# Cache dependencies
COPY --link requirements.txt ./server/
RUN pip install --no-cache-dir -r server/requirements.txt
# Copy source
COPY --link . ./server
CMD ["fastapi", "run", "server/app.py"]
