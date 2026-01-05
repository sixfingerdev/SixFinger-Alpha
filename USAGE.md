# SixFinger-Alpha Usage Guide

## Quick Start Examples

### 1. Command-Line Usage

#### Basic Task Execution
```bash
python autonomous_agent.py "Your task here"
```

#### Real-World Examples

**Research Task:**
```bash
python autonomous_agent.py "Research the latest developments in quantum computing and explain their practical applications"
```

**Code Generation:**
```bash
python autonomous_agent.py "Write a Python function that implements binary search with proper error handling"
```

**Content Writing:**
```bash
python autonomous_agent.py "Write an informative article about the environmental impact of renewable energy"
```

**Analysis Task:**
```bash
python autonomous_agent.py "Analyze the pros and cons of microservices architecture versus monolithic architecture"
```

### 2. Interactive Mode

For a guided experience with example tasks:

```bash
python example.py
```

This will present you with:
- Option 1: Compact version (minimal API code)
- Option 2: Full autonomous agent with enhanced features

### 3. Programmatic Usage

#### Basic Import and Usage
```python
from autonomous_agent import AutonomousAgent

# Create an agent
agent = AutonomousAgent()

# Execute a task
agent.parse_and_execute("Explain how neural networks work")
```

#### Using Specific Methods
```python
from autonomous_agent import AutonomousAgent

agent = AutonomousAgent()

# Research mode
agent.research("latest AI trends in 2024")

# Code generation mode
agent.generate_code("Create a REST API endpoint for user authentication")

# Writing mode
agent.write("The future of autonomous vehicles", style="informative")

# Analysis mode
content = "Your text content here..."
agent.analyze(content)
```

#### Custom Model Configuration
```python
from autonomous_agent import AutonomousAgent

# Use a different model (if available)
agent = AutonomousAgent(model="custom-model-name")
```

#### Non-Streaming Mode
```python
from autonomous_agent import AutonomousAgent

agent = AutonomousAgent()

# Get complete response without streaming
response = agent.query("What is machine learning?", stream=False)
print(response)
```

### 4. Compact Version (Original API Code)

If you want to use the minimal version directly:

```python
import requests as r
import json

# Your prompt
prompt = "Explain quantum entanglement"

for l in r.post(
    "https://api.deepinfra.com/v1/openai/chat/completions",
    headers={"X-Deepinfra-Source": "web-page"},
    json={
        "model": "deepseek-ai/DeepSeek-R1-0528-Turbo",
        "messages": [{"role": "user", "content": prompt}],
        "stream": 1
    },
    stream=1
).iter_lines():
    if l and (c := l.decode()[6:]) != "[DONE]":
        try:
            print(json.loads(c)['choices'][0]['delta']['content'], end='')
        except:
            0
print()  # New line
```

## Use Case Scenarios

### Software Development

**Debug Code:**
```bash
python autonomous_agent.py "Debug this Python code: [paste your code]"
```

**Generate Tests:**
```bash
python autonomous_agent.py "Write unit tests for a user authentication function"
```

**Code Review:**
```bash
python autonomous_agent.py "Review this code and suggest improvements: [paste code]"
```

### Learning and Research

**Learn Concepts:**
```bash
python autonomous_agent.py "Explain machine learning algorithms in simple terms"
```

**Research Topics:**
```bash
python autonomous_agent.py "Research and summarize the history of artificial intelligence"
```

**Compare Technologies:**
```bash
python autonomous_agent.py "Compare React vs Vue.js for web development"
```

### Content Creation

**Blog Posts:**
```bash
python autonomous_agent.py "Write a blog post about sustainable technology practices"
```

**Documentation:**
```bash
python autonomous_agent.py "Write API documentation for a REST endpoint"
```

**Tutorials:**
```bash
python autonomous_agent.py "Create a tutorial on getting started with Python"
```

### Business Analysis

**Market Research:**
```bash
python autonomous_agent.py "Analyze current trends in the AI industry"
```

**Strategic Planning:**
```bash
python autonomous_agent.py "Analyze the risks and benefits of adopting cloud infrastructure"
```

**Competitive Analysis:**
```bash
python autonomous_agent.py "Compare different project management methodologies"
```

## Tips for Best Results

1. **Be Specific**: The more specific your task description, the better the results
   - ❌ "Write code"
   - ✅ "Write a Python function that validates email addresses using regex"

2. **Provide Context**: Include relevant context in your prompt
   - ✅ "As a web developer, I need to understand how to implement JWT authentication"

3. **Break Down Complex Tasks**: For complex requirements, break them into steps
   - ✅ "First explain the concept, then provide an example, and finally show how to implement it"

4. **Specify Format**: If you need a specific format, mention it
   - ✅ "Provide the answer in bullet points"
   - ✅ "Format the code with comments explaining each section"

## Troubleshooting

### Import Errors
If you get import errors, ensure dependencies are installed:
```bash
pip install -r requirements.txt
```

### Network Issues
The agent requires internet connectivity to access the DeepInfra API. Check:
- Internet connection
- Firewall settings
- API availability

### Rate Limiting
If you encounter rate limits:
- Wait a few moments between requests
- The free tier has usage limits
- Consider reducing request frequency

## Running Tests

To verify the installation:
```bash
python test_agent.py
```

To validate the implementation:
```bash
python validate.py
```

## Advanced Usage

### Integration in Your Projects

```python
# example_integration.py
from autonomous_agent import AutonomousAgent

class MyApplication:
    def __init__(self):
        self.ai_agent = AutonomousAgent()
    
    def get_ai_assistance(self, user_query):
        """Get AI assistance for user queries."""
        return self.ai_agent.parse_and_execute(user_query)
    
    def generate_documentation(self, code):
        """Generate documentation for code."""
        prompt = f"Generate documentation for this code:\n\n{code}"
        return self.ai_agent.query(prompt)

# Use in your app
app = MyApplication()
result = app.get_ai_assistance("How do I implement caching?")
```

### Error Handling

```python
from autonomous_agent import AutonomousAgent

agent = AutonomousAgent()

try:
    result = agent.parse_and_execute("Your task")
    if result is None:
        print("Task failed - check network connection")
    else:
        print(f"Success: {result}")
except Exception as e:
    print(f"Error: {e}")
```

## Getting Help

- Check the README.md for overview and features
- Run tests: `python test_agent.py`
- Validate setup: `python validate.py`
- Review examples: `python example.py`

## Best Practices

1. **Always validate critical code** generated by the AI
2. **Review research results** for accuracy
3. **Test generated code** before using in production
4. **Provide feedback** in your prompts if initial results aren't quite right
5. **Iterate** - you can refine prompts based on initial responses

---

Happy coding with SixFinger-Alpha! 🚀
