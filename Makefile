.PHONY: setup install test clean docker-build docker-up docker-down docker-logs help

# Default target
help:
	@echo "Luno MCP Server - Available Commands:"
	@echo ""
	@echo "  setup         - Run initial setup (install dependencies, create .env)"
	@echo "  install       - Install Python dependencies only"
	@echo "  test          - Run test client (STDIO mode)"
	@echo "  test-ws       - Run test client (WebSocket mode)"
	@echo "  run           - Run server in STDIO mode"
	@echo "  run-ws        - Run server in WebSocket mode"
	@echo "  docker-build  - Build Docker image"
	@echo "  docker-up     - Start server with Docker Compose"
	@echo "  docker-down   - Stop Docker containers"
	@echo "  docker-logs   - View Docker container logs"
	@echo "  clean         - Clean up build artifacts"
	@echo ""

# Initial setup
setup:
	@./setup.sh

# Install dependencies
install:
	@echo "Installing dependencies..."
	@uv pip install -r requirements.txt

# Test the server
test:
	@echo "Testing server (STDIO mode)..."
	@python test_client.py --transport stdio

test-ws:
	@echo "Testing server (WebSocket mode)..."
	@python test_client.py --transport websocket

# Run the server
run:
	@echo "Starting server in STDIO mode..."
	@python -m src.main --transport stdio

run-ws:
	@echo "Starting server in WebSocket mode..."
	@python -m src.main --transport websocket

# Docker commands
docker-build:
	@echo "Building Docker image..."
	@docker build -t luno-mcp-server .

docker-up:
	@echo "Starting server with Docker Compose..."
	@docker compose up -d

docker-down:
	@echo "Stopping Docker containers..."
	@docker compose down

docker-logs:
	@echo "Viewing Docker container logs..."
	@docker compose logs -f

# Clean up
clean:
	@echo "Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@rm -rf build/
	@rm -rf dist/
	@echo "Clean up complete!"
