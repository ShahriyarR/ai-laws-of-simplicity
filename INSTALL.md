# Installing the Laws of Simplicity Skill

This guide explains how to install the Laws of Simplicity skill in any AI coding agent that supports custom skills.

## Overview

The Laws of Simplicity skill is a standalone module that guides AI agents to apply John Maeda's 10 Laws of Simplicity throughout the software development lifecycle. To use it, you need to copy the skill directory to your agent's skills folder.

## Installation Steps

### 1. Clone or Download This Repository

First, obtain a copy of this repository:

```bash
# Using git
git clone https://github.com/AI-Provenance/ai-laws-of-simplicity.git
cd ai-laws-of-simplicity

# Or download as ZIP and extract
```

### 2. Locate Your Agent's Skills Directory

Different agents store skills in different locations. Find the appropriate directory for your agent:

#### OpenCode
- `~/.config/opencode/skills/`

#### Cursor
- `~/.cursor/skills/` or check Cursor settings for skills directory

#### GitHub Copilot
- Skills are typically configured through the Copilot extension settings

#### Other Agents
Consult your agent's documentation for where to place custom skills

### 3. Copy the Skill Directory

Copy the `skills/laws-of-simplicity/` directory from this repository to your agent's skills directory:

```bash
# Example for OpenCode
cp -r skills/laws-of-simplicity/ ~/.config/opencode/skills/

# Example for a generic agent
cp -r skills/laws-of-simplicity/ /path/to/your/agent/skills/
```

### 4. Verify Installation

After copying, verify that the skill is available in your agent:

1. Restart or reload your agent if necessary
2. Check the list of available skills (method varies by agent)
3. You should see "laws-of-simplicity" in the list

### 5. Using the Skill

Once installed, you can invoke the skill in your agent:

```
skill laws-of-simplicity
```

The skill will provide guidance on applying the Laws of Simplicity to your current development task.

## Updating the Skill

To update to a newer version:

1. Pull the latest changes from this repository
2. Repeat the copy step to overwrite the existing skill directory
3. Restart your agent if needed

## Uninstalling

To remove the skill:

1. Delete the `laws-of-simplicity` directory from your agent's skills folder
2. Restart your agent

## Troubleshooting

- **Skill not showing up**: Verify the directory was copied to the correct location and contains a `SKILL.md` file
- **Agent doesn't recognize the skill**: Check that your agent version supports custom skills
- **Errors when invoking**: Ensure the `SKILL.md` file has proper formatting (YAML frontmatter followed by markdown)

## Support

If you encounter issues, please file an issue in this repository's issue tracker.

---

*This skill is based on "The Laws of Simplicity" by John Maeda*