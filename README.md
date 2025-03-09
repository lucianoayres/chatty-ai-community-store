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
tags: # List of tags (at least one required)
  - "tag1"
  - "tag2"
author: "Author Name" # Optional, max 40 characters
```

### Required Fields

All agent YAML files must include:

- `name`: Agent name (max 40 chars)
- `emoji`: Exactly one character
- `description`: Short description (max 65 chars)
- `system_message`: System message (max 1500 chars)
- `label_color`: Label color (max 15 chars)
- `text_color`: Text color (max 15 chars)
- `is_default`: Boolean value
- `tags`: List of valid tags (at least one required)

### Optional Fields

- `author`: Author name (max 40 chars)

### Tags

Tags must be selected from the predefined list in [`tags.json`](tags.json). Available categories include:

- featured
- historical
- cultural
- fictional
- intellectuals
- scientists
- mythological
- creative
- artists
- writers
- philosophers
- musicians
- movie_characters
- professional
- business
- technical
- supportive
- analytical
- spiritual
- sports
- educational
- miscellaneous

### Color Configuration

The `label_color` and `text_color` fields use ANSI escape codes for 256-color terminal display:

- Format: `\u001b[38;5;{color_number}m`
- Color numbers range from 0-255
- Examples:
  - `\u001b[38;5;75m`: Light blue
  - `\u001b[38;5;252m`: Light gray
  - `\u001b[38;5;196m`: Red

## Store Configuration

The [`store_config.json`](store_config.json) file defines how agents are organized and displayed in the Chatty AI storefront interface. It controls the categorization, ordering, and visibility of agents.

### Structure

```json
{
  "storefrontSettings": {
    "categories": [
      {
        "name": "Category Name",
        "description": "Category description shown to users",
        "tags": ["tag1", "tag2"],
        "enabled": true,
        "maxItems": 8
      }
      // Additional categories...
    ]
  }
}
```

### Category Fields

Each category in the store configuration includes:

- `name`: Display name for the category
- `description`: Short description of the category
- `tags`: List of tags used to filter agents for this category
- `enabled`: Boolean flag to show/hide the category
- `maxItems`: Maximum number of agents to display in this category
- `timeWindowDays`: (Optional) For time-based categories like "New Arrivals"

### Default Categories

The store includes several predefined categories:

- Featured
- New Arrivals
- Creative Minds
- Scientific Experts
- Philosophical Thinkers
- Historical Figures
- Fictional Characters
- Professional Guides
- Sports & Athletics
- Spiritual & Mystical

## Validation Workflow

The repository includes GitHub Actions workflows that automatically validate YAML files and update the agent index:

### Agent YAML Validator

This workflow runs whenever YAML files in the `agents/` directory are added or modified:

1. Validates each YAML file against the schema
2. Checks for required fields
3. Verifies that tags are valid
4. Provides detailed error information if validation fails

### Agent Index Updater

This workflow runs when a pull request with YAML changes is merged:

1. Identifies which agent YAML files were changed
2. Runs the agent manager script to update the index
3. Commits and pushes any changes to the agent_index.json file
4. Provides a summary of the update

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
├── .github/workflows/      # GitHub Actions workflows
│   ├── agent-yaml-validator.yml  # Validates YAML files
│   └── agent-index-updater.yml   # Updates the agent index
├── store_config.json       # Storefront configuration settings
└── agent_index.json        # Generated index of all valid agents
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
3. Include at least one valid tag from the tags.json file
4. Submit a pull request with your new agent
5. The validation workflow will check your agent for errors
6. Once merged, the index updater workflow will update the agent_index.json file

### Schema Updates

- [`schemas/agent.schema.yaml`](schemas/agent.schema.yaml): Defines the structure for agent YAML files
- [`schemas/index.schema.json`](schemas/index.schema.json): Defines the structure for the agent_index.json file
- [`tags.json`](tags.json): Defines the valid tags for agent categorization
- [`store_config.json`](store_config.json): Defines the storefront categories and display settings
- All schemas are enforced by the validation workflow and agent manager tool

## Contributing

When contributing new agents or modifications:

1. Ensure all YAML files follow the schema
2. Include at least one valid tag from the tags.json file
3. Submit a pull request with your changes
4. The validation workflow will check for errors
5. Fix any validation errors before merging
6. After merging, the index updater workflow will update the agent_index.json file

## License

This project is licensed under the MIT License. See the [`LICENSE`](LICENSE) for details.
