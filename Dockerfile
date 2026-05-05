FROM selenium/standalone-chrome:4.18.1-20240224

USER root

RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    && ln -s /usr/bin/python3 /usr/bin/python \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements-test.txt ./
RUN PIP_BREAK_SYSTEM_PACKAGES=1 pip3 install --no-cache-dir -r requirements.txt -r requirements-test.txt

COPY . .

EXPOSE 5000

# Important: Use python3
CMD ["python3", "app.py"]
