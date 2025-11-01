FROM python:3.14.0-alpine3.22
COPY . ./server
RUN pip install --no-cache-dir -r server/requirements.txt
CMD ["fastapi", "run", "server/app.py"]
