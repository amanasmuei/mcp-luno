#!/usr/bin/env python3
"""
Simple validation script to check if our FastMCP configuration is correct.
This runs basic syntax checks without requiring full FastMCP installation.
"""

import ast
import sys
import os
from pathlib import Path


def validate_python_syntax(file_path):
    """Validate Python syntax for a file."""
    try:
        with open(file_path, "r") as f:
            source = f.read()
        ast.parse(source)
        print(f"✅ {file_path}: Syntax valid")
        return True
    except SyntaxError as e:
        print(f"❌ {file_path}: Syntax error - {e}")
        return False
    except Exception as e:
        print(f"❌ {file_path}: Error - {e}")
        return False


def validate_import_structure(file_path):
    """Check if imports look correct."""
    try:
        with open(file_path, "r") as f:
            content = f.read()

        # Check for FastMCP specific imports
        if "src/luno_mcp_server/server.py" in str(file_path):
            if "from fastmcp import FastMCP" not in content:
                print(f"❌ {file_path}: Missing FastMCP import")
                return False
            if "@mcp.tool()" not in content:
                print(f"❌ {file_path}: Missing @mcp.tool() decorators")
                return False
            print(f"✅ {file_path}: FastMCP imports and decorators found")

        if "tests/test_server.py" in str(file_path):
            if "from fastmcp import Client" not in content:
                print(f"❌ {file_path}: Missing FastMCP Client import")
                return False
            print(f"✅ {file_path}: FastMCP Client import found")

        if "test_client.py" in str(file_path):
            if "from fastmcp import Client" not in content:
                print(f"❌ {file_path}: Missing FastMCP Client import")
                return False
            print(f"✅ {file_path}: FastMCP Client import found")

        return True
    except Exception as e:
        print(f"❌ {file_path}: Error checking imports - {e}")
        return False


def validate_setup_py():
    """Validate setup.py configuration."""
    try:
        with open("setup.py", "r") as f:
            content = f.read()

        checks = [
            ("fastmcp>=2.0.0", "FastMCP dependency"),
            ('python_requires=">=3.10"', "Python 3.10+ requirement"),
            ("src.main:run_sync", "Correct entry point"),
        ]

        all_good = True
        for check, description in checks:
            if check in content:
                print(f"✅ setup.py: {description} found")
            else:
                print(f"❌ setup.py: {description} missing")
                all_good = False

        return all_good
    except Exception as e:
        print(f"❌ setup.py: Error - {e}")
        return False


def validate_requirements():
    """Validate requirements.txt."""
    try:
        with open("requirements.txt", "r") as f:
            content = f.read()

        if "fastmcp>=2.0.0" in content:
            print("✅ requirements.txt: FastMCP dependency found")
            return True
        else:
            print("❌ requirements.txt: FastMCP dependency missing")
            return False
    except Exception as e:
        print(f"❌ requirements.txt: Error - {e}")
        return False


def main():
    """Run all validations."""
    print("=== Validating FastMCP Configuration ===\n")

    all_passed = True

    # Files to check
    files_to_check = [
        "src/main.py",
        "src/luno_mcp_server/server.py",
        "tests/test_server.py",
        "test_client.py",
    ]

    # Syntax validation
    print("1. Checking Python syntax...")
    for file_path in files_to_check:
        if os.path.exists(file_path):
            if not validate_python_syntax(file_path):
                all_passed = False
        else:
            print(f"⚠️  {file_path}: File not found")

    print("\n2. Checking import structure...")
    for file_path in files_to_check:
        if os.path.exists(file_path):
            if not validate_import_structure(file_path):
                all_passed = False

    print("\n3. Checking setup.py...")
    if not validate_setup_py():
        all_passed = False

    print("\n4. Checking requirements.txt...")
    if not validate_requirements():
        all_passed = False

    print(f"\n=== Validation Summary ===")
    if all_passed:
        print("🎉 All validations passed! Configuration looks good.")
        print("\nNext steps:")
        print("1. Install Python 3.10+ if not available")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Run tests: python -m pytest tests/")
        print("4. Test server: python test_client.py")
    else:
        print("❌ Some validations failed. Please fix the issues above.")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
