"""
Sample client to test the Luno MCP server.
"""

import os
import json
import asyncio
import logging
from subprocess import Popen, PIPE

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Sample MCP request for getting server capabilities
SAMPLE_REQUEST = {
    "jsonrpc": "2.0",
    "method": "describe_capabilities",
    "params": {},
    "id": 1,
}


async def test_mcp_server():
    """Test the MCP server with a sample request."""
    # Start the server
    logger.info("Starting the MCP server process...")
    process = Popen(
        ["python", "-m", "src.main"],
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        text=True,
        bufsize=1,
    )

    try:
        # Send the request
        request_json = json.dumps(SAMPLE_REQUEST)
        logger.info(f"Sending request: {request_json}")
        process.stdin.write(f"{request_json}\n")
        process.stdin.flush()

        # Read the response
        response = process.stdout.readline().strip()
        logger.info(f"Received response: {response}")

        # Parse the response
        response_obj = json.loads(response)

        # Check the response
        if "result" in response_obj:
            print("\n✅ Server is working correctly!")
            print(f"\nServer capabilities:")
            print(f"  Name: {response_obj['result']['name']}")
            print(f"  Version: {response_obj['result']['version']}")
            print(f"  Description: {response_obj['result']['description']}")
            print(f"\nAvailable methods:")
            for method in response_obj["result"]["methods"]:
                print(f"  - {method}")
        else:
            print("\n❌ Server returned an error.")
            print(f"Error: {response_obj.get('error')}")

    finally:
        # Terminate the server
        process.terminate()
        process.wait()


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
