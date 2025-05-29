#!/usr/bin/env python3
"""
Global Donation Setup Script for the Luno MCP Server project.
Run this script to easily update your global donation links that work worldwide.
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
    print("🌍 Luno MCP Server - Global Donation Setup")
    print("=" * 60)
    print("Setting up donation options that work worldwide! 🚀")

    # Get user input
    print("\n📝 Please provide your global donation information:")

    # Buy Me a Coffee (Most popular)
    print("\n☕ Buy Me a Coffee (Most popular - works in 190+ countries)")
    coffee_username = input("Buy Me a Coffee username: ").strip()
    if coffee_username:
        coffee_url = f"https://buymeacoffee.com/{coffee_username}"
    else:
        coffee_url = "https://buymeacoffee.com/yourusername"

    # Ko-fi
    print("\n🌍 Ko-fi (Creator-friendly platform)")
    kofi_username = input("Ko-fi username: ").strip()
    if kofi_username:
        kofi_url = f"https://ko-fi.com/{kofi_username}"
    else:
        kofi_url = "https://ko-fi.com/yourusername"

    # PayPal.me (simpler than donation buttons)
    print("\n💳 PayPal.me (Direct payments)")
    paypal_username = input("PayPal.me username: ").strip()
    if paypal_username:
        paypal_url = f"https://paypal.me/{paypal_username}"
    else:
        paypal_url = "https://paypal.me/yourusername"

    # GitHub
    print("\n🐙 GitHub")
    github_username = input("GitHub username: ").strip()
    github_repo = (
        input("GitHub repository name (default: luno-mcp): ").strip() or "luno-mcp"
    )
    if github_username:
        github_url = f"https://github.com/{github_username}/{github_repo}"
        github_sponsors_url = f"https://github.com/sponsors/{github_username}"
    else:
        github_url = "https://github.com/yourusername/luno-mcp"
        github_sponsors_url = "https://github.com/sponsors/yourusername"

    # Crypto addresses (optional)
    print("\n🪙 Cryptocurrency addresses (optional, press Enter to skip):")
    btc_address = input("Bitcoin (BTC) address: ").strip() or "your-btc-address-here"
    eth_address = input("Ethereum (ETH) address: ").strip() or "your-eth-address-here"
    lightning_address = (
        input("Lightning Network address (user@domain.com): ").strip()
        or "yourlightningaddress@domain.com"
    )

    # Optional services
    print("\n🎁 Optional services:")
    amazon_wishlist = input("Amazon Wishlist ID (optional): ").strip()
    if amazon_wishlist:
        amazon_url = f"https://amazon.com/hz/wishlist/ls/{amazon_wishlist}"
    else:
        amazon_url = "https://amazon.com/hz/wishlist/ls/YOUR_WISHLIST_ID"

    # Your name for attribution
    your_name = input("\n👤 Your name for attribution: ").strip() or "Your Name"

    print(f"\n🔄 Updating files with global donation options...")

    # Define replacements
    replacements = {
        "https://buymeacoffee.com/yourusername": coffee_url,
        "https://ko-fi.com/yourusername": kofi_url,
        "https://paypal.me/yourusername": paypal_url,
        "https://github.com/yourusername/luno-mcp": github_url,
        "https://github.com/sponsors/yourusername": github_sponsors_url,
        "your-btc-address-here": btc_address,
        "your-eth-address-here": eth_address,
        "yourlightningaddress@domain.com": lightning_address,
        "https://amazon.com/hz/wishlist/ls/YOUR_WISHLIST_ID": amazon_url,
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
    print("\n🌍 Global Donation Options Summary:")
    print(f"  ☕ Buy Me a Coffee: {coffee_url}")
    print(f"  🌍 Ko-fi: {kofi_url}")
    print(f"  💳 PayPal.me: {paypal_url}")
    print(f"  💖 GitHub Sponsors: {github_sponsors_url}")
    if amazon_wishlist:
        print(f"  🎁 Amazon Wishlist: {amazon_url}")

    print("\n📋 Next steps:")
    print("1. Commit your changes to git")
    print("2. Push to GitHub to enable GitHub Pages")
    print("3. Your donation page will be available at:")
    if github_username:
        pages_url = f"https://{github_username}.github.io/{github_repo}/donate.html"
        print(f"   {pages_url}")
    else:
        print("   https://yourusername.github.io/luno-mcp/donate.html")
    print("4. Set up GitHub Sponsors in your repository settings")
    print("5. Create accounts on Buy Me a Coffee and Ko-fi")
    print("6. Test all donation links")
    print("7. Restart Claude Desktop to use the updated support tool")

    print(
        f"\n🎉 Users can now ask Claude: 'How can I support this project?' for global donation options!"
    )
    print("💡 All these platforms work internationally with multiple payment methods!")


if __name__ == "__main__":
    main()
