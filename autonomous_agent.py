#!/usr/bin/env python3
"""
Autonomous AI Agent for Complex Task Execution
Uses DeepSeek-R1 for intelligent task parsing and execution
"""

import requests as r
import json
import sys
from typing import Optional, Dict, Any


class AutonomousAgent:
    """
    Autonomous AI agent that can parse tasks and execute various operations:
    - Web research
    - Code generation
    - Writing and analysis
    - Task decomposition
    """
    
    def __init__(self, model: str = "deepseek-ai/DeepSeek-R1-0528-Turbo"):
        self.model = model
        self.api_url = "https://api.deepinfra.com/v1/openai/chat/completions"
        self.headers = {"X-Deepinfra-Source": "web-page"}
        
    def query(self, prompt: str, stream: bool = True) -> Optional[str]:
        """
        Send a query to the AI model and get a response.
        
        Args:
            prompt: The user's prompt/task
            stream: Whether to stream the response
            
        Returns:
            Complete response text or None on error
        """
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": 1 if stream else 0
        }
        
        try:
            response = r.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                stream=stream
            )
            response.raise_for_status()
            
            if stream:
                return self._handle_stream(response)
            else:
                return response.json()['choices'][0]['message']['content']
                
        except (r.RequestException, ValueError, KeyError) as e:
            print(f"\nError querying AI: {e}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"\nUnexpected error: {e}", file=sys.stderr)
            return None
    
    def _handle_stream(self, response) -> str:
        """
        Handle streaming response from the API.
        
        Args:
            response: The streaming response object
            
        Returns:
            Complete response text
        """
        full_response = []
        
        for line in response.iter_lines():
            if line and (chunk := line.decode()[6:]) != "[DONE]":
                try:
                    data = json.loads(chunk)
                    content = data['choices'][0]['delta'].get('content', '')
                    if content:
                        print(content, end='', flush=True)
                        full_response.append(content)
                except (json.JSONDecodeError, KeyError, IndexError):
                    # Ignore malformed chunks or incomplete data during streaming
                    pass
        
        print()  # New line after streaming
        return ''.join(full_response)
    
    def parse_and_execute(self, task: str) -> Optional[str]:
        """
        Parse a task description and execute it.
        
        The agent will:
        1. Understand the task requirements
        2. Determine the best approach (web research, code, writing, analysis)
        3. Execute the task
        4. Deliver the results
        
        Args:
            task: The task description from the user
            
        Returns:
            Task execution results
        """
        # Enhance the prompt to guide the AI in task execution
        enhanced_prompt = f"""You are an autonomous AI agent. Analyze and execute the following task:

Task: {task}

Please:
1. Parse and understand what is being asked
2. Determine if this requires web research, code generation, writing, or analysis
3. Execute the task thoroughly
4. Provide a clear, actionable response

Execute the task now:"""
        
        print(f"🤖 Autonomous Agent Processing Task...\n")
        print(f"📋 Task: {task}\n")
        print("=" * 60)
        print("🎯 Response:\n")
        
        result = self.query(enhanced_prompt, stream=True)
        print("\n" + "=" * 60)
        print("✅ Task Complete\n")
        
        return result
    
    def research(self, topic: str) -> Optional[str]:
        """Execute web research on a topic."""
        prompt = f"Research and provide comprehensive information about: {topic}"
        return self.parse_and_execute(prompt)
    
    def generate_code(self, requirements: str) -> Optional[str]:
        """Generate code based on requirements."""
        prompt = f"Generate code for the following requirements: {requirements}"
        return self.parse_and_execute(prompt)
    
    def write(self, topic: str, style: str = "informative") -> Optional[str]:
        """Write content on a topic."""
        prompt = f"Write {style} content about: {topic}"
        return self.parse_and_execute(prompt)
    
    def analyze(self, content: str) -> Optional[str]:
        """Analyze provided content."""
        prompt = f"Analyze the following content:\n\n{content}"
        return self.parse_and_execute(prompt)


def main():
    """Command-line interface for the autonomous agent."""
    print("=" * 60)
    print("🚀 SixFinger Autonomous AI Agent")
    print("=" * 60)
    print()
    
    if len(sys.argv) < 2:
        print("Usage: python autonomous_agent.py <task>")
        print("\nExamples:")
        print('  python autonomous_agent.py "Research quantum computing"')
        print('  python autonomous_agent.py "Write a Python function to sort a list"')
        print('  python autonomous_agent.py "Analyze the benefits of AI"')
        sys.exit(1)
    
    task = ' '.join(sys.argv[1:])
    agent = AutonomousAgent()
    agent.parse_and_execute(task)


if __name__ == "__main__":
    main()
