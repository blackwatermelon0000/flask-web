FROM selenium/standalone-chrome:4.18.1-20240224

USER root

# Install Python
RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first (so pip layer is cached separately)
COPY requirements.txt requirements-test.txt ./
RUN pip3 install --no-cache-dir \
    flask selenium==4.18.1 pytest \
    --break-system-packages

# Copy app code last
COPY . .

EXPOSE 5000
CMD ["bash"]
