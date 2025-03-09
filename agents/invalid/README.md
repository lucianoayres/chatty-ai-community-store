# Invalid Agent Files

This directory contains agent files that failed validation but were preserved for reference.

## Why Files are Here

Files in this directory were automatically moved here by the quarantine workflow when they:
1. Failed validation checks
2. Were pushed directly to the main branch

## How to Fix

1. Review the validation errors (available in the associated GitHub issue)
2. Make the necessary corrections
3. Create a PR with the fixed file in the main `agents/` directory

## Naming Convention

Files here follow the pattern: `original_filename_TIMESTAMP.yaml`
The timestamp helps avoid name collisions if the same file is quarantined multiple times.
