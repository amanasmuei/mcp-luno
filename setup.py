from setuptools import setup, find_packages

setup(
    name="luno-mcp-server",
    version="0.1.0",
    description="Model Context Protocol server for the Luno cryptocurrency exchange API",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "pydantic>=2.0.0",
        "httpx>=0.24.0",
        "python-dotenv>=1.0.0",
        "jsonrpc>=1.15.0",
        "websockets>=15.0.0",
    ],
    entry_points={
        "console_scripts": [
            "luno-mcp-server=main:main",
        ],
    },
)
