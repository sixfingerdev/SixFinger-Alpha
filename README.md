# SixFinger-Alpha 🚀

Autonomous AI agent for complex task execution using DeepSeek-R1 model.

## Overview

SixFinger-Alpha is an autonomous AI agent that can parse tasks and execute various operations including:
- 🔍 **Web Research**: Gather and synthesize information on any topic
- 💻 **Code Generation**: Write code based on requirements
- ✍️ **Content Writing**: Create informative, creative, or technical content
- 📊 **Analysis**: Analyze data, text, or concepts in depth

The agent uses the powerful DeepSeek-R1-0528-Turbo model via DeepInfra API to understand tasks and deliver intelligent responses.

## Features

- **Task Parsing**: Automatically understands and categorizes user requests
- **Multi-Modal Execution**: Handles research, coding, writing, and analysis tasks
- **Streaming Responses**: Real-time output as the AI generates responses
- **Simple Interface**: Easy-to-use command-line and programmatic APIs
- **Compact Core**: Built on efficient, minimal API code

## Installation

```bash
# Clone the repository
git clone https://github.com/sixfingerdev/SixFinger-Alpha.git
cd SixFinger-Alpha

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Command-Line Usage

```bash
# Simple task execution
python autonomous_agent.py "Research the latest AI developments"

# Code generation
python autonomous_agent.py "Write a Python function to reverse a string"

# Analysis
python autonomous_agent.py "Analyze the impact of quantum computing"
```

### Interactive Mode

```bash
python example.py
```

The interactive demo offers two modes:
1. **Compact Version**: The minimal API code from the original specification
2. **Autonomous Agent**: Full-featured agent with enhanced capabilities

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
├── autonomous_agent.py    # Main agent implementation
├── example.py            # Interactive examples and demos
├── requirements.txt      # Python dependencies
└── README.md            # Documentation
```

### AutonomousAgent Class

The core `AutonomousAgent` class provides:

- `parse_and_execute(task)`: Main entry point for task execution
- `query(prompt)`: Direct API interaction with streaming
- `research(topic)`: Specialized web research mode
- `generate_code(requirements)`: Code generation mode
- `write(topic, style)`: Content writing mode
- `analyze(content)`: Analysis mode

## Use Cases

### 1. Development Assistant
```bash
python autonomous_agent.py "Write unit tests for a user authentication function"
```

### 2. Research Tool
```bash
python autonomous_agent.py "Research best practices for microservices architecture"
```

### 3. Content Creator
```bash
python autonomous_agent.py "Write a blog post about sustainable technology"
```

### 4. Code Analyzer
```bash
python autonomous_agent.py "Analyze this code for potential improvements: [your code]"
```

## How It Works

1. **Task Input**: User provides a task description
2. **Parse**: Agent analyzes the task to understand intent and requirements
3. **Execute**: Agent determines the best approach (research/code/write/analyze)
4. **Stream**: Real-time output as the AI generates the response
5. **Deliver**: Complete, actionable results delivered to the user

## API Rate Limits

This agent uses the DeepInfra API with DeepSeek-R1 model. Be mindful of:
- Rate limits imposed by DeepInfra
- Streaming responses may take time for complex tasks
- Network connectivity requirements

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

**Built with ❤️ by SixFinger Dev**
