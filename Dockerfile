FROM python:3.11-slim

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

# Set default environment variables for FastMCP
ENV MCP_TRANSPORT=streamable-http
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000

# Expose the default port
EXPOSE 8000

# The default command to run the FastMCP server
CMD ["python", "-m", "src.main", "--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8000"]
