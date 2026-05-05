FROM selenium/standalone-chrome:4.18.1-20240224

USER root

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements-test.txt ./

# Install packages (use env var instead of flag for compatibility)
RUN PIP_BREAK_SYSTEM_PACKAGES=1 pip3 install --no-cache-dir -r requirements.txt -r requirements-test.txt

# Copy the rest of the app
COPY . .

EXPOSE 5000
CMD ["bash"]
