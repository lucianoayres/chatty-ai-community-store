# Chatty AI Community Store

![Chatty AICommunity Store Banner](./images/chatty_ai_community_store_banner.png)

## About

A collection of AI agent configurations for [Chatty AI](https://github.com/lucianoayres/chatty-ai) - a terminal app that enables engaging conversations with AI personalities ranging from historical figures to domain experts.

## Agent Configuration

Each agent is defined in a YAML file within the [`agents/`](agents/) directory. These configurations determine how characters behave in Chatty AI conversations. The format is defined in [`schemas/agent.schema.yaml`](schemas/agent.schema.yaml):

```yaml
name: "Agent Name" # Max 40 characters
description: "Description" # Max 65 characters
emoji: "🤖" # Single emoji character
system_message: "..." # Max 1500 characters - Defines agent personality and expertise
label_color: "\u001b[38;5;75m" # ANSI color code for name display in terminal
text_color: "\u001b[38;5;252m" # ANSI color code for message text in terminal
is_default: false # Boolean flag
```

### Color Configuration

The `label_color` and `text_color` fields use ANSI escape codes for 256-color terminal display:

- Format: `\u001b[38;5;{color_number}m`
- Color numbers range from 0-255
- Examples:
  - `\u001b[38;5;75m`: Light blue
  - `\u001b[38;5;252m`: Light gray
  - `\u001b[38;5;196m`: Red

## Agent Manager Tool

The project includes a tool for managing agent configurations, located in [`tools/agent_manager/`](tools/agent_manager/). This tool ensures all agents are properly formatted for use in Chatty AI:

1. Validates all agent YAML files against the schema
2. Generates and updates the [`agent_index.json`](agent_index.json) file
3. Maintains creation timestamps for agents
4. Reports validation errors and provides summaries

### Usage

To manage agents and update the index:

```bash
cd tools/agent_manager
./manage_agents.sh
```

The tool will:

- Create a Python virtual environment if needed
- Install required dependencies
- Validate all agent YAML files
- Update the agent_index.json file
- Provide a summary of changes

### Error Handling

- Validation errors are logged to `sync_errors.log`
- The tool exits with status code 1 if critical errors occur
- Invalid agent files are skipped but reported in the summary

## Index File

The [`agent_index.json`](agent_index.json) file contains a list of all valid agents and is automatically maintained by the agent manager. This file is used by Chatty AI to:

- Load available agents
- Display agent listings
- Access agent metadata for conversations

It includes:

- Version information
- Total count of agents
- List of agent entries with:
  - ID (derived from filename)
  - Name
  - Description
  - Emoji
  - Creation timestamp

## Project Structure

```
.
├── agents/                  # YAML files containing agent configurations
├── schemas/                 # JSON and YAML schema definitions
│   ├── agent.schema.yaml   # Schema for individual agent YAML files
│   └── index.schema.json   # Schema for the agent_index.json file
├── tools/                  # Project tooling
│   └── agent_manager/     # Tool for managing agent configurations
│       ├── manage_agents.sh    # Main entry point script
│       └── src/               # Python source code
│           ├── generator.py   # Index generation module
│           ├── validator.py   # YAML validation module
│           └── update_index.py # Main Python script
└── agent_index.json             # Generated index of all valid agents
```

## Development

### Requirements

- Python 3.x
- bash shell
- Required Python packages (automatically installed):
  - pyyaml
  - jsonschema
  - yamale

### Adding New Agents

1. Create a new YAML file in the [`agents/`](agents/) directory
2. Follow the schema defined in [`schemas/agent.schema.yaml`](schemas/agent.schema.yaml)
3. Run the agent manager tool to validate and index the new agent
4. Test the agent in Chatty AI to ensure proper behavior

### Schema Updates

- [`schemas/agent.schema.yaml`](schemas/agent.schema.yaml): Defines the structure for agent YAML files
- [`schemas/index.schema.json`](schemas/index.schema.json): Defines the structure for the agent_index.json file
- Both schemas are enforced by the agent manager tool

## Contributing

When contributing new agents or modifications:

1. Ensure all YAML files follow the schema
2. Run the agent manager tool to validate changes
3. Check the error log if validation fails
4. Verify the agent_index.json is updated correctly
5. Test new agents in Chatty AI before submitting

## License

This project is licensed under the MIT License. See the [`LICENSE`](LICENSE) for details.
