FROM python:3.11-slim

# Install Chrome and ChromeDriver
RUN apt-get update && apt-get install -y \
     wget curl unzip gnupg ca-certificates \
     && install -m 0755 -d /etc/apt/keyrings \
     && wget -q -O /etc/apt/keyrings/google-linux.gpg https://dl.google.com/linux/linux_signing_key.pub \
     && gpg --dearmor -o /etc/apt/keyrings/google-linux.gpg /etc/apt/keyrings/google-linux.gpg \
     && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-linux.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
         > /etc/apt/sources.list.d/google-chrome.list \
     && apt-get update \
     && apt-get install -y google-chrome-stable \
     && apt-get clean

# Install matching ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | sed 's/Google Chrome //') \
    && DRIVER_VERSION=$(curl -sS "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$(echo $CHROME_VERSION | cut -d. -f1)") \
    && wget -q "https://chromedriver.storage.googleapis.com/${DRIVER_VERSION}/chromedriver_linux64.zip" \
    && unzip chromedriver_linux64.zip -d /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm chromedriver_linux64.zip

WORKDIR /app

# Copy everything
COPY . .

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt -r requirements-test.txt

# Expose the port
EXPOSE 5000

CMD ["bash"]