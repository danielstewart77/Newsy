# Use the official Alpine Linux as the base image
FROM alpine:latest

# Install Python, pip, and venv support
RUN apk add --no-cache python3 py3-pip python3-dev build-base

# Set the working directory in the container
WORKDIR /usr/src/app

# Create and activate a virtual environment
RUN python3 -m venv /usr/src/app/venv
ENV PATH="/usr/src/app/venv/bin:$PATH"

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies inside the virtual environment
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of your application's code
COPY . .

# Expose the port your app runs on
EXPOSE 80

# Command to run the Flask application using the virtual environment's Python
#CMD ["python", "news.py"]
ENTRYPOINT ["venv/bin/python3", "news.py"]