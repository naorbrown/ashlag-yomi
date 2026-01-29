# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | ✅        |
| < 1.0   | ❌        |

## Reporting a Vulnerability

**Do NOT open a public issue for security vulnerabilities.**

Instead, please email the maintainer directly with:

1. **Description** of the vulnerability
2. **Steps to reproduce** the issue
3. **Impact assessment** — what could an attacker do?

You can expect a response within **48 hours**.

## Security Best Practices

### For Contributors

- **Never commit secrets** — `TELEGRAM_BOT_TOKEN` and other credentials must stay out of version control
- **Use `.env` files** — Store secrets locally, never in the repository
- **Review dependencies** — Run `pip-audit` before adding new packages

### For Deployers

- **Use HTTPS** — All production deployments should use secure connections
- **Rotate tokens** — If you suspect a token leak, regenerate immediately via @BotFather
- **Minimal permissions** — Only give the bot admin access where necessary

### Built-in Protections

- **Rate limiting**: 5 requests per minute per user (prevents abuse)
- **Input validation**: Pydantic models validate all data
- **No user data storage**: The bot doesn't store personal information

## Acknowledgments

We appreciate security researchers who help keep Ashlag Yomi safe. Responsible disclosure is always welcomed.
