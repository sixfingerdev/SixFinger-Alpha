# SixFinger-Alpha

Advanced AI API Platform with full-featured Flask web application.

## Overview

SixFinger-Alpha is now a complete web platform offering:
- **User Authentication**: Secure login/signup with password hashing
- **Subscription Management**: Multiple pricing tiers with Stripe integration
- **Developer Portal**: API key management and usage tracking
- **Admin Panel**: Comprehensive user and system management
- **Multi-Currency**: Support for USD and TRY (1$ = 47₺)
- **Enterprise Security**: CSRF protection, rate limiting, secure headers
- **Analytics**: Detailed usage statistics and monitoring
- **RESTful API**: AI-powered endpoints for research, code generation, and analysis

The platform uses the powerful DeepSeek-R1-0528-Turbo model via DeepInfra API to deliver intelligent AI capabilities.

## Features

### Web Platform
- **Authentication System**: Secure user registration and login with email verification
- **Subscription Plans**: Free, Starter ($9), Pro ($49), Enterprise ($299)
- **Payment Processing**: Stripe integration with USD and TRY currency support
- **Developer Portal**: 
  - Generate and manage API keys
  - View usage statistics
  - Monitor request history
- **Admin Panel**:
  - User management
  - Subscription control
  - System analytics
  - Usage monitoring
- **Security**:
  - Password hashing with bcrypt
  - CSRF protection
  - Rate limiting
  - Secure session management
  - XSS protection headers

### API Capabilities
- **Research**: Comprehensive web research on any topic
- **Code Generation**: Generate code in multiple languages
- **Analysis**: Deep analysis of data and content
- **Custom Queries**: Flexible AI-powered responses

## Installation

```bash
# Clone the repository
git clone https://github.com/sixfingerdev/SixFinger-Alpha.git
cd SixFinger-Alpha

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the application
python run.py
```

Visit `http://localhost:5000` in your browser.

## Quick Start

### Web Application

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure Environment**:
```bash
cp .env.example .env
# Edit .env with your settings (Stripe keys, email config, etc.)
```

3. **Run the Application**:
```bash
python run.py
```

Visit `http://localhost:5000` to access the web interface.

4. **Create Admin User**:
```bash
python create_admin.py
```

### Command-Line Usage (Legacy)

The original autonomous agent is still available:

```bash
# Simple task execution
python autonomous_agent.py "Research the latest AI developments"

# Interactive mode
python example.py
```

### Programmatic Usage

```python
from autonomous_agent import AutonomousAgent

# Create an agent instance
agent = AutonomousAgent()

# Execute a task
agent.parse_and_execute("Explain how neural networks learn")

# Or use specific methods
agent.research("quantum computing applications")
agent.generate_code("Create a REST API endpoint")
agent.write("The future of AI", style="informative")
agent.analyze("Your content here...")
```

## Core Technology

The agent is built on this compact, efficient code:

```python
import requests as r, json

for l in r.post(
    "https://api.deepinfra.com/v1/openai/chat/completions",
    headers={"X-Deepinfra-Source": "web-page"},
    json={
        "model": "deepseek-ai/DeepSeek-R1-0528-Turbo",
        "messages": [{"role": "user", "content": "x"}],
        "stream": 1
    },
    stream=1
).iter_lines():
    if l and (c := l.decode()[6:]) != "[DONE]":
        try:
            print(json.loads(c)['choices'][0]['delta']['content'], end='')
        except:
            0
```

This minimal code is wrapped in a robust, user-friendly interface that provides task parsing, error handling, and specialized execution modes.

## Architecture

```
SixFinger-Alpha/
├── app/
│   ├── __init__.py              # Application factory
│   ├── models.py                # Database models
│   ├── blueprints/              # Application modules
│   │   ├── auth.py              # Authentication
│   │   ├── main.py              # Main routes
│   │   ├── api.py               # API endpoints
│   │   ├── admin.py             # Admin panel
│   │   ├── developer.py         # Developer portal
│   │   └── subscription.py      # Subscription management
│   ├── templates/               # HTML templates
│   └── static/                  # CSS, JS, images
├── autonomous_agent.py          # Original AI agent (CLI)
├── example.py                   # Interactive examples
├── run.py                       # Application entry point
├── config.py                    # Configuration
├── requirements.txt             # Dependencies
└── README.md                    # Documentation
```

## API Usage

### Authentication
All API requests require authentication using an API key:

```bash
curl -H "X-API-Key: your_api_key_here" \
     https://yourdomain.com/api/v1/query
```

### Endpoints

**POST /api/v1/query** - General AI query
```bash
curl -X POST https://yourdomain.com/api/v1/query \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain quantum computing"}'
```

**POST /api/v1/research** - Research a topic
```bash
curl -X POST https://yourdomain.com/api/v1/research \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Latest AI developments"}'
```

**POST /api/v1/code** - Generate code
```bash
curl -X POST https://yourdomain.com/api/v1/code \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"requirements": "Create a REST API endpoint"}'
```

**GET /api/v1/usage** - Check API usage
```bash
curl -H "X-API-Key: your_api_key" \
     https://yourdomain.com/api/v1/usage
```

## Subscription Plans

| Plan       | Price (USD) | Price (TRY) | Daily Limit | Monthly Limit |
|------------|-------------|-------------|-------------|---------------|
| Free       | $0          | 0₺          | 100         | 1,000         |
| Starter    | $9          | 423₺        | 1,000       | 25,000        |
| Pro        | $49         | 2,303₺      | 10,000      | 250,000       |
| Enterprise | $299        | 14,053₺     | Unlimited   | Unlimited     |

*Exchange rate: 1 USD = 47 TRY*

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## License

MIT License - feel free to use this in your own projects!

## Acknowledgments

- **DeepSeek AI** for the powerful R1 model
- **DeepInfra** for providing accessible API access
- The open-source community for inspiration and tools

---

**Built with passion by SixFinger Dev**
