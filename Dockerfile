# Use a specific, stable Airflow base image to ensure reproducible builds and avoid 'latest' tag pitfalls
FROM apache/airflow:2.10.1

# Set environment variables to enforce UTF-8 encoding throughout the container
ENV PYTHONUTF8=1 
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV ENV=docker

# Switch to root user to install Python dependencies with necessary privileges
#USER root

# Copy the requirements file to the container
COPY ./requirements.txt /requirements.txt

# Install Python dependencies without cache to keep the image lean
RUN pip install --no-cache-dir -r /requirements.txt

# Drop back to the airflow user for security best practices
USER airflow