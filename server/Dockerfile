# Use the official Python image as the base image
FROM python:3

# copy everything
COPY . .

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the start.sh script when the container starts
CMD ["fastapi run app.py"]