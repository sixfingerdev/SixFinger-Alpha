# Contributing to SixFinger Alpha

Thank you for your interest in contributing to SixFinger Alpha! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Your environment (OS, Python version, etc.)

### Suggesting Features

Feature suggestions are welcome! Please create an issue with:
- Clear description of the feature
- Use case and benefits
- Possible implementation approach

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Write/update tests if applicable
5. Update documentation
6. Commit your changes (`git commit -m 'Add feature'`)
7. Push to your branch (`git push origin feature/your-feature`)
8. Create a Pull Request

## Development Setup

1. Clone the repository
2. Create a virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and configure
5. Run tests: `python test_flask_app.py`
6. Start the development server: `python run.py`

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions small and focused
- Write comments for complex logic

## Testing

- Test your changes thoroughly
- Add tests for new features
- Ensure existing tests pass
- Test security implications

## Security

- Never commit sensitive data (passwords, API keys, etc.)
- Follow security best practices
- Report security vulnerabilities privately to support@sixfinger.dev

## Documentation

- Update README.md if needed
- Update API documentation for API changes
- Update CHANGELOG.md
- Comment complex code

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to create an issue for any questions or reach out to support@sixfinger.dev

Thank you for contributing!
