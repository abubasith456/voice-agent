# LiveKit Voice Agent - Clean Modular Architecture

## Overview

This project implements a clean, modular architecture for a LiveKit voice agent system with configurable flows based on participant metadata.

## Architecture

### File Structure

```
/agents
  ├── base_agent.py       # Abstract BaseAgent class
  ├── basic_agent.py      # BasicAgent (no auth)
  ├── multi_agent_new.py  # Orchestrator class
  ├── auth_agent.py       # Handles authentication
  ├── query_agent.py      # Handles queries/details
  ├── helpline_agent.py   # Handles helpline connection
/main.py                  # Entry point with flow selection
```

### Agent Flow Configuration

The system supports two main flows based on `participant.metadata.is_auth_based`:

#### 1. MultiAgent Flow (`is_auth_based = true`)
- **AuthAgent**: Handles OTP authentication
- **QueryAgent**: Manages user queries and account details
- **HelplineAgent**: Provides human support connection
- **MultiAgent**: Orchestrates transitions between agents

#### 2. BasicAgent Flow (`is_auth_based = false`)
- **BasicAgent**: Simple voice-to-voice assistance
- No authentication required
- Limited capabilities for general support

## Core Components

### BaseAgent (Abstract)
- Abstract base class for all agents
- Provides common initialization and session management
- Enforces consistent interface across all agents

### MultiAgent (Orchestrator)
- Manages composition of three sub-agents
- Handles routing and transitions between agents
- Maintains conversation context across agent switches
- Uses composition pattern (not inheritance)

### Individual Agents

#### AuthAgent
- Handles 4-digit OTP authentication
- Manages authentication state
- Switches to QueryAgent on success

#### QueryAgent
- Processes user queries after authentication
- Provides account information access
- Offers helpline connection when needed

#### HelplineAgent
- Human support specialist simulation
- Handles complex customer issues
- Manages session termination

#### BasicAgent
- Simple conversational assistant
- No authentication or complex routing
- General customer service support

## Entry Point Logic

The `main.py` file implements clean flow selection:

```python
# Choose agent based on metadata
if is_auth_based:
    agent = MultiAgent(job_context=ctx, user_name=user_name, user_id=user_id)
else:
    agent = BasicAgent(job_context=ctx, user_name=user_name, user_id=user_id)
```

## Key Design Principles

1. **Single Responsibility**: Each agent has a specific, well-defined role
2. **Composition over Inheritance**: MultiAgent uses composition to manage sub-agents
3. **Clean Separation**: Orchestration logic is separate from agent logic
4. **Extensibility**: Easy to add new agents or modify existing ones
5. **Consistent Interface**: All agents inherit from BaseAgent

## Usage

### Starting the System

```bash
python main.py
```

### Metadata Configuration

For auth-based flow:
```json
{
  "userName": "John Doe",
  "userId": "u123",
  "is_auth_based": true
}
```

For basic flow:
```json
{
  "userName": "John Doe",
  "userId": "u123",
  "is_auth_based": false
}
```

## Extending the Architecture

To add a new agent:

1. Create a new file in `/agents/`
2. Inherit from `BaseAgent`
3. Implement `get_base_instructions()` method
4. Add to `MultiAgent` composition if needed
5. Update `__init__.py` exports

## Benefits

- **Modularity**: Each agent is self-contained and testable
- **Maintainability**: Clear separation of concerns
- **Scalability**: Easy to add new capabilities
- **Flexibility**: Configurable flows based on requirements
- **Clean Code**: Follows SOLID principles and clean architecture patterns