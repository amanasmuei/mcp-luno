# 💖 Donation Setup Guide

This guide explains how to set up the "Buy Me a Coffee" donation features for your Luno MCP Server project.

## 🚀 Quick Setup

### 1. Run the Setup Script

```bash
python setup_donations.py
```

This interactive script will ask for:
- PayPal Hosted Button ID or donation URL
- Buy Me a Coffee username
- GitHub username and repository name
- Bitcoin and Ethereum addresses (optional)
- Your name for attribution

### 2. Get Your PayPal Donation Button

1. Go to [PayPal Donate Button](https://www.paypal.com/donate/buttons)
2. Sign in to your PayPal account
3. Create a new donation button
4. Copy the Hosted Button ID from the generated code
5. Use this ID in the setup script

### 3. Set Up Buy Me a Coffee

1. Create an account at [Buy Me a Coffee](https://buymeacoffee.com)
2. Choose your username
3. Customize your page
4. Use your username in the setup script

## 📁 Files Created/Modified

The setup process updates these files:

- **`README.md`** - Adds sponsorship section with donation links
- **`docs/donate.html`** - Beautiful donation page with PayPal/crypto options
- **`docs/_config.yml`** - GitHub Pages configuration
- **`src/luno_mcp_server/server.py`** - Adds `get_support_info()` MCP tool
- **`.github/workflows/deploy-pages.yml`** - Auto-deploys donation page

## 🌐 GitHub Pages Setup

### Enable GitHub Pages

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Pages**
3. Under **Source**, select **GitHub Actions**
4. The workflow will automatically deploy your donation page

### Access Your Donation Page

Once deployed, your donation page will be available at:
```
https://yourusername.github.io/your-repo-name/donate.html
```

## 🛠️ MCP Tool Usage

After setup, users can ask Claude:

- *"How can I support this project?"*
- *"Show me donation options"*
- *"How do I contribute to this project?"*

The `get_support_info()` tool will provide comprehensive donation information.

## 💳 PayPal Integration

### Option 1: Hosted Button (Recommended)

1. Create a donation button at PayPal
2. Use the Hosted Button ID in setup
3. Automatic currency conversion
4. Professional appearance

### Option 2: Direct PayPal Link

Use a direct PayPal.me link:
```
https://paypal.me/yourusername
```

## 🪙 Cryptocurrency Donations

### Supported Coins

- **Bitcoin (BTC)** - Most popular option
- **Ethereum (ETH)** - Second most common
- **Any Luno-supported coin** - Relevant to your project

### Security Tips

- Use dedicated donation addresses
- Consider using a hardware wallet
- Never share private keys
- Monitor donations regularly

## 🎨 Customization

### Donation Page Styling

Edit `docs/donate.html` to customize:
- Colors and branding
- Additional payment methods
- Project-specific messaging
- Social media links

### README Badges

Add more donation badges:
```markdown
[![PayPal](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](your-paypal-link)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](your-coffee-link)
```

## 📊 Analytics and Tracking

### Track Donations

- PayPal provides transaction history
- Buy Me a Coffee has built-in analytics
- GitHub Stars/Forks indicate project popularity
- Monitor crypto addresses with blockchain explorers

### Success Metrics

- Monthly donation amount
- Number of supporters
- GitHub repository engagement
- User feedback and testimonials

## 🔧 Troubleshooting

### Common Issues

**Donation page not loading:**
- Check GitHub Pages is enabled
- Verify workflow completed successfully
- Ensure `docs/` folder contains all files

**PayPal button not working:**
- Verify Hosted Button ID is correct
- Check PayPal account is verified
- Ensure donation buttons are enabled

**MCP tool not working:**
- Restart Claude Desktop after changes
- Check server.py syntax is correct
- Verify tool is properly registered

### Getting Help

1. Check GitHub Actions logs for deployment issues
2. Test donation links manually
3. Validate HTML/CSS in donation page
4. Review PayPal/Buy Me a Coffee documentation

## 🎉 Success Tips

### Maximize Donations

1. **Clear Value Proposition**: Explain how donations help
2. **Multiple Options**: Offer various payment methods
3. **Recognition**: Thank supporters publicly (with permission)
4. **Updates**: Share development progress with supporters
5. **Transparency**: Show how funds are used

### Community Building

- Engage with supporters on social media
- Create a Discord/Slack for contributors
- Offer early access to new features
- Provide supporter-only documentation

---

**Thank you for supporting open source development! 🚀**