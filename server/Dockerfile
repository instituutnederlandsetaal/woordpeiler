# Use the official Python image as the base image
FROM python:3.12-bookworm

# copy everything
COPY . ./server

# Install the Python dependencies
RUN pip install --no-cache-dir -r server/requirements.txt

# Run the start.sh script when the container starts
CMD ["fastapi", "run", "server/app.py"]