FROM python:3.13.5-alpine3.21

COPY . ./server

RUN pip install --no-cache-dir -r server/requirements.txt

CMD ["fastapi", "run", "server/app.py"]