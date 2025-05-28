#!/bin/bash
# Setup script for Luno MCP Server

set -e

echo "🚀 Setting up Luno MCP Server..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
uv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

# Install dependencies
echo "📥 Installing dependencies..."
uv pip install -r requirements.txt

# Setup environment file
if [ ! -f .env ]; then
    echo "⚙️  Creating environment file..."
    cp .env.example .env
    echo "✏️  Please edit .env file with your Luno API credentials"
else
    echo "✅ Environment file already exists"
fi

# Generate certificates for SSL (optional)
if [ ! -d "certs" ]; then
    echo "🔐 Generating SSL certificates..."
    ./generate_certificates.sh
else
    echo "✅ SSL certificates already exist"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Luno API credentials"
echo "2. Test the server: python test_client.py"
echo "3. Run the server: python -m src.main"
echo ""
echo "For Docker usage:"
echo "  docker compose up -d"
echo ""
