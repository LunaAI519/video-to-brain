# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | ✅ Yes             |
| < 0.2   | ❌ No              |

## Reporting a Vulnerability

If you discover a security vulnerability in video-to-brain, please report it responsibly.

### How to Report

**Please do NOT open a public GitHub issue for security vulnerabilities.**

Instead, send an email to: **luna@randanai.com**

Include:
- A description of the vulnerability
- Steps to reproduce (if possible)
- The potential impact
- Any suggested fix (optional but appreciated)

### What to Expect

- **Acknowledgment**: Within 48 hours of your report
- **Assessment**: We'll evaluate the severity within 1 week
- **Fix**: Critical issues will be patched as soon as possible
- **Credit**: We'll credit you in the release notes (unless you prefer to remain anonymous)

### Scope

The following are in scope:
- **Bot token exposure** — any way the Telegram bot token could be leaked
- **API key exposure** — any way LLM API keys could be leaked
- **File system access** — unauthorized read/write outside the configured vault
- **Injection attacks** — command injection via video filenames or metadata
- **Dependency vulnerabilities** — known CVEs in dependencies

The following are out of scope:
- Issues in Telegram's infrastructure
- Issues in third-party LLM APIs (OpenAI, etc.)
- Issues requiring physical access to the server

## Security Best Practices for Users

1. **Never commit `.env` files** — they contain your API keys
2. **Use environment variables** — don't hardcode tokens in code
3. **Run with minimal permissions** — don't run the bot as root
4. **Keep dependencies updated** — run `pip install --upgrade -r requirements.txt` regularly
5. **Restrict bot access** — use Telegram's bot privacy settings to limit who can send videos

## Dependencies

We regularly check for known vulnerabilities in our dependencies. If you notice an outdated dependency with a known CVE, please open an issue or email us.

---

Thank you for helping keep video-to-brain and its users safe! 🙏
