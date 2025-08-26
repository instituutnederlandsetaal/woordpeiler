FROM python:3.13.7-alpine3.22
COPY . ./server
RUN pip install --no-cache-dir -r server/requirements.txt
CMD ["fastapi", "run", "server/app.py"]
