FROM apache/airflow:2.10.1

# Set environment variables to enforce UTF-8 encoding throughout the container
ENV PYTHONUTF8=1 
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV ENV=docker

# Copy the requirements file to the container
COPY requirements.txt .

# Install Python dependencies without cache to keep the image lean
RUN pip install --no-cache-dir -r requirements.txt