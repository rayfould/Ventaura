# Use an official Python runtime as a base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install the necessary packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 (optional, depends on your app)
#EXPOSE 5000

# Run the application
CMD ["python", "./main.py"]
