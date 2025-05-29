#!/usr/bin/env python3
"""
Setup script to customize donation links for the Luno MCP Server project.
Run this script to easily update your PayPal, Buy Me a Coffee, and crypto addresses.
"""

import os
import re


def update_file(filepath: str, replacements: dict) -> bool:
    """Update a file with the given replacements."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content
        for old, new in replacements.items():
            content = content.replace(old, new)

        if content != original_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ Updated {filepath}")
            return True
        else:
            print(f"ℹ️  No changes needed for {filepath}")
            return False
    except Exception as e:
        print(f"❌ Error updating {filepath}: {e}")
        return False


def main():
    print("🚀 Luno MCP Server - Donation Setup")
    print("=" * 50)

    # Get user input
    print("\n📝 Please provide your donation information:")

    # PayPal
    paypal_id = input("PayPal Hosted Button ID (or full donate URL): ").strip()
    if paypal_id and not paypal_id.startswith("http"):
        paypal_url = f"https://www.paypal.com/donate?hosted_button_id={paypal_id}"
    elif paypal_id:
        paypal_url = paypal_id
    else:
        paypal_url = (
            "https://www.paypal.com/donate?hosted_button_id=YOUR_PAYPAL_BUTTON_ID"
        )

    # Buy Me a Coffee
    coffee_username = input("Buy Me a Coffee username: ").strip()
    if coffee_username:
        coffee_url = f"https://buymeacoffee.com/{coffee_username}"
    else:
        coffee_url = "https://buymeacoffee.com/yourusername"

    # GitHub
    github_username = input("GitHub username: ").strip()
    github_repo = (
        input("GitHub repository name (default: luno-mcp): ").strip() or "luno-mcp"
    )
    if github_username:
        github_url = f"https://github.com/{github_username}/{github_repo}"
    else:
        github_url = "https://github.com/yourusername/luno-mcp"

    # Crypto addresses (optional)
    print("\n🪙 Crypto donation addresses (optional, press Enter to skip):")
    btc_address = input("Bitcoin (BTC) address: ").strip() or "your-btc-address-here"
    eth_address = input("Ethereum (ETH) address: ").strip() or "your-eth-address-here"

    # Your name for attribution
    your_name = input("\n👤 Your name for attribution: ").strip() or "Your Name"

    print(f"\n🔄 Updating files...")

    # Define replacements
    replacements = {
        "YOUR_PAYPAL_BUTTON_ID": (
            paypal_id
            if paypal_id and not paypal_id.startswith("http")
            else "YOUR_PAYPAL_BUTTON_ID"
        ),
        "https://www.paypal.com/donate?hosted_button_id=YOUR_PAYPAL_BUTTON_ID": paypal_url,
        "https://buymeacoffee.com/yourusername": coffee_url,
        "https://github.com/yourusername/luno-mcp": github_url,
        "your-btc-address-here": btc_address,
        "your-eth-address-here": eth_address,
        "Your Name": your_name,
        "yourusername": github_username if github_username else "yourusername",
    }

    # Files to update
    files_to_update = [
        "README.md",
        "docs/donate.html",
        "src/luno_mcp_server/server.py",
        "docs/_config.yml",
    ]

    updated_files = 0
    for filepath in files_to_update:
        if os.path.exists(filepath):
            if update_file(filepath, replacements):
                updated_files += 1
        else:
            print(f"⚠️  File not found: {filepath}")

    print(f"\n✅ Setup complete! Updated {updated_files} files.")
    print("\n📋 Next steps:")
    print("1. Commit your changes to git")
    print("2. Push to GitHub to enable GitHub Pages")
    print("3. Your donation page will be available at:")
    print(
        f"   {github_url.replace('github.com', 'github.io').replace(f'/{github_repo}', f'/{github_repo}/docs/donate.html')}"
    )
    print("4. Test the donation links")
    print("5. Restart Claude Desktop to use the new support tool")

    print(
        f"\n🎉 Users can now ask Claude: 'How can I support this project?' to see donation options!"
    )


if __name__ == "__main__":
    main()
