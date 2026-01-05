#!/usr/bin/env python3
"""
Interactive example demonstrating the autonomous agent capabilities.
This script shows how to use the agent for different task types.
"""

from autonomous_agent import AutonomousAgent


def demo_compact_version():
    """
    Demonstrates the compact version from the problem statement.
    This is the minimal code to interact with DeepSeek API.
    """
    print("=" * 60)
    print("📦 COMPACT VERSION (Original Code)")
    print("=" * 60)
    print()
    
    # Original compact code from problem statement
    import requests as r
    import json
    
    prompt = input("Enter your task: ")
    
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
    print("\n")


def demo_autonomous_agent():
    """
    Demonstrates the full autonomous agent with enhanced capabilities.
    """
    print("=" * 60)
    print("🤖 AUTONOMOUS AGENT VERSION")
    print("=" * 60)
    print()
    
    agent = AutonomousAgent()
    
    # Example tasks
    examples = [
        ("Code Generation", "Write a Python function to calculate fibonacci numbers"),
        ("Web Research", "What are the latest developments in AI agents?"),
        ("Analysis", "Analyze the pros and cons of autonomous AI systems"),
        ("Writing", "Write a short explanation of how neural networks work")
    ]
    
    print("Available example tasks:")
    for i, (category, task) in enumerate(examples, 1):
        print(f"{i}. [{category}] {task}")
    print(f"{len(examples) + 1}. Custom task")
    print()
    
    choice = input("Select a task (1-5) or press Enter for custom: ").strip()
    
    if choice.isdigit() and 1 <= int(choice) <= len(examples):
        category, task = examples[int(choice) - 1]
        print(f"\n✨ Executing: {task}\n")
        agent.parse_and_execute(task)
    else:
        task = input("Enter your custom task: ")
        agent.parse_and_execute(task)


def main():
    """Main interactive menu."""
    print("\n" + "=" * 60)
    print("🚀 SixFinger Autonomous AI Agent - Interactive Demo")
    print("=" * 60)
    print()
    print("Choose a demo mode:")
    print("1. Compact Version (Original API code)")
    print("2. Autonomous Agent (Full featured)")
    print()
    
    choice = input("Enter your choice (1 or 2): ").strip()
    print()
    
    if choice == "1":
        demo_compact_version()
    elif choice == "2":
        demo_autonomous_agent()
    else:
        print("Invalid choice. Please run again and select 1 or 2.")


if __name__ == "__main__":
    main()
