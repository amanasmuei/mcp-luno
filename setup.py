from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="luno-mcp-server",
    version="0.2.0",
    description="Modern FastMCP server for the Luno cryptocurrency exchange API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Luno MCP Team",
    author_email="support@example.com",
    url="https://github.com/your-username/luno-mcp-server",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "fastmcp>=2.0.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "httpx>=0.24.0",
        "python-dotenv>=1.0.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.5.0",
        ],
        "logging": [
            "structlog>=23.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "luno-mcp-server=main:run_sync",
            "luno-mcp-dev=main:dev_mode",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Office/Business :: Financial",
    ],
    keywords="mcp, fastmcp, luno, cryptocurrency, api, server, bitcoin, ethereum",
    project_urls={
        "Bug Reports": "https://github.com/your-username/luno-mcp-server/issues",
        "Source": "https://github.com/your-username/luno-mcp-server",
        "Documentation": "https://github.com/your-username/luno-mcp-server#readme",
    },
)
