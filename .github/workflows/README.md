# GitHub Workflows

## Agent YAML Validator

This workflow automatically validates agent YAML files in the `agents` directory when they are added or modified.

### Trigger

The workflow is triggered when:

- A push contains changes to any `.yaml` or `.yml` file in the `agents` directory
- A pull request contains changes to any `.yaml` or `.yml` file in the `agents` directory

### Validation Process

The workflow:

1. Identifies which YAML files were changed
2. Runs the validator script on each changed file
3. Reports any validation errors directly in the GitHub Actions interface
4. For pull requests, also validates all YAML files in the `agents` directory
5. Posts validation results as a comment on the pull request

### Error Reporting

Validation errors are displayed in multiple ways:

- Directly in the GitHub Actions workflow output
- As annotations on the specific files with issues
- As a detailed comment on the pull request
- With detailed information about which fields are missing or invalid

### Pull Request Comments

For pull requests, the workflow will:

1. Create a comment with validation results for each changed file
2. Update the comment if the workflow runs again (rather than creating multiple comments)
3. Include a summary of validation status
4. Show detailed error information for any files that failed validation

This makes it easy for contributors to see validation issues directly in the PR without having to navigate to the Actions tab.

### Example Error

```
Error: YAML schema validation error: Error validating data './agents/ab.yaml' with schema 'schemas/agent.schema.yaml'
        name: Required field missing
Error: Missing required fields: name
```

This indicates that the file `./agents/ab.yaml` is missing the required `name` field.

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
