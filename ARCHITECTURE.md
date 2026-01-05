# SixFinger-Alpha Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │  CLI Interface │  │ Example Demo │  │ Python API      │ │
│  │ (main script)  │  │ (interactive)│  │ (programmatic)  │ │
│  └────────┬───────┘  └──────┬───────┘  └────────┬────────┘ │
└───────────┼──────────────────┼───────────────────┼──────────┘
            │                  │                   │
            └──────────────────┼───────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────┐
│                  AutonomousAgent Class                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Core Methods:                                        │   │
│  │  • parse_and_execute() - Main task processor         │   │
│  │  • query() - API communication                       │   │
│  │  • _handle_stream() - Response streaming             │   │
│  │                                                       │   │
│  │  Specialized Methods:                                │   │
│  │  • research() - Web research tasks                   │   │
│  │  • generate_code() - Code generation                 │   │
│  │  • write() - Content creation                        │   │
│  │  • analyze() - Content analysis                      │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────┬───────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────┐
│              DeepInfra API Integration Layer                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Compact Core (from problem statement):              │   │
│  │                                                       │   │
│  │  for l in r.post(...).iter_lines():                 │   │
│  │    if l and (c := l.decode()[6:]) != "[DONE]":      │   │
│  │      try:                                            │   │
│  │        print(json.loads(c)['choices'][0]            │   │
│  │              ['delta']['content'], end='')          │   │
│  │      except: 0                                       │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               │ HTTPS/JSON
                               │
┌──────────────────────────────▼───────────────────────────────┐
│           DeepInfra API (External Service)                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  DeepSeek-R1-0528-Turbo Model                        │   │
│  │  • Natural language understanding                    │   │
│  │  • Task decomposition                                │   │
│  │  • Code generation                                   │   │
│  │  • Research synthesis                                │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────┘
```

## Data Flow

```
1. User Input
   ↓
2. Task Parsing
   ↓
3. Prompt Enhancement
   ↓
4. API Request (Streaming)
   ↓
5. Response Processing
   ↓
6. Output Display
   ↓
7. Result Delivery
```

## Component Interaction

```
┌─────────────┐         ┌──────────────┐         ┌───────────┐
│    User     │────────>│ Autonomous   │────────>│ DeepInfra │
│             │  Task   │   Agent      │ Request │    API    │
│             │         │              │         │           │
│             │<────────│              │<────────│           │
│             │ Result  │              │Response │           │
└─────────────┘         └──────────────┘         └───────────┘
```

## Execution Modes

### 1. Direct Streaming (Compact Version)
```
User → API → Stream → Console
(Minimal overhead, maximum speed)
```

### 2. Autonomous Agent (Full Version)
```
User → Agent → Task Parser → Enhanced Prompt → API → 
       Stream Handler → Response Aggregator → Output
(Enhanced features, better UX)
```

## Task Processing Pipeline

```
┌──────────────────────────────────────────────────────────┐
│ 1. Input Task: "Write a Python function to sort a list" │
└────────────────────────┬─────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────┐
│ 2. Parse: Identify as CODE GENERATION task               │
└────────────────────────┬─────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────┐
│ 3. Enhance Prompt: Add context and instructions          │
└────────────────────────┬─────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────┐
│ 4. Execute: Send to DeepSeek-R1 model                    │
└────────────────────────┬─────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────┐
│ 5. Stream: Display response in real-time                 │
└────────────────────────┬─────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────┐
│ 6. Deliver: Complete Python function with explanation    │
└──────────────────────────────────────────────────────────┘
```

## Key Features

### [TASK] Task Classification
- Automatically determines task type
- Routes to appropriate execution mode
- Enhances prompts for better results

###  Streaming Output
- Real-time response display
- No waiting for complete response
- Better user experience

###  Flexible API
- Command-line interface
- Interactive mode
- Programmatic usage
- Compact version for power users

### ️ Error Handling
- Network error recovery
- API error handling
- Graceful degradation

## Technology Stack

```
┌─────────────────────────────────────────┐
│ Python 3.8+ (Walrus operator support)   │
├─────────────────────────────────────────┤
│ requests - HTTP client                  │
├─────────────────────────────────────────┤
│ json - Response parsing                 │
├─────────────────────────────────────────┤
│ DeepInfra API - Model hosting           │
├─────────────────────────────────────────┤
│ DeepSeek-R1-0528-Turbo - AI model      │
└─────────────────────────────────────────┘
```

## Performance Characteristics

- **Response Time**: Streaming starts within 1-2 seconds
- **Throughput**: Depends on API rate limits
- **Memory**: Minimal footprint (streaming architecture)
- **Network**: Requires stable internet connection

## Extensibility Points

```python
class AutonomousAgent:
    # Easy to extend with:
    # 1. Custom models
    # 2. Additional task types
    # 3. Custom preprocessing
    # 4. Response post-processing
    # 5. Integration with other services
```

## Future Enhancements (Potential)

- [ ] Multi-turn conversations
- [ ] Context persistence
- [ ] Custom model fine-tuning
- [ ] Plugin system
- [ ] Web UI
- [ ] API key management
- [ ] Response caching
- [ ] Multi-language support
