FROM python:3.9-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY src/ src/
COPY setup.py .

# Install the package
RUN pip install -e .

# Copy the example env file and rename it (will be overridden by actual env file when running)
COPY .env.example .env

# The default command to run the server
CMD ["python", "-m", "src.main"]
