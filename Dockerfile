FROM python:3.11-slim

# Install Chrome — pipe key directly, no /dev/tty needed
RUN apt-get update && apt-get install -y \
        wget gnupg ca-certificates \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub \
       | gpg --dearmor > /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] \
       http://dl.google.com/linux/chrome/deb/ stable main" \
       > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver that matches Chrome
RUN CHROME_VER=$(google-chrome --version | grep -oP '\d+' | head -1) \
    && wget -q "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VER}.0.0.0/linux64/chromedriver-linux64.zip" \
       -O /tmp/chromedriver.zip \
    || wget -q "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VER}" -O /tmp/cdver \
    && CDVER=$(cat /tmp/cdver 2>/dev/null || echo "") \
    && wget -q "https://chromedriver.storage.googleapis.com/${CDVER}/chromedriver_linux64.zip" \
       -O /tmp/chromedriver.zip \
    && unzip -o /tmp/chromedriver.zip -d /tmp/ \
    && find /tmp -name "chromedriver" -exec mv {} /usr/local/bin/chromedriver \; \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf /tmp/chromedriver*

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir flask selenium==4.18.1 pytest

EXPOSE 5000
CMD ["bash"]
