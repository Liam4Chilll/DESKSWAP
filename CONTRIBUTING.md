# Contributing to Desk Swap

First off, thank you for considering contributing to Desk Swap! 🎉

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples**
- **Describe the behavior you observed and what you expected**
- **Include screenshots if relevant**
- **Note your environment** (OS, Docker version, browser)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Use a clear and descriptive title**
- **Provide a detailed description of the suggested enhancement**
- **Explain why this enhancement would be useful**
- **List examples of how it would be used**

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. Ensure your code follows the existing style
4. Update documentation if needed
5. Write a clear commit message

#### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/deskswap.git
cd deskswap

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install flask

# Run locally
python app.py
```

#### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions small and focused

#### Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests when relevant

### Testing

Before submitting a PR, test your changes:

```bash
# Test with Docker
docker compose up --build

# Test different scenarios:
# - Large files
# - Special characters in filenames
# - Deep directory structures
# - Multiple concurrent downloads
```

## Project Structure

```
deskswap/
├── app.py              # Main Flask application
├── templates/          # HTML templates
│   ├── index.html     # Main interface
│   └── error.html     # Error pages
├── Dockerfile          # Container image
├── docker-compose.yml  # Deployment config
└── README.md          # Documentation
```

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all.

### Our Standards

**Positive behavior includes:**
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**
- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

## Questions?

Feel free to open an issue with your question or reach out to the maintainers.

Thank you for contributing! 🚀
