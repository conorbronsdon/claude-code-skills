---
name: skill-creator
description: Generate a new Claude Code skill file from a plain-language description. Scaffolds the SKILL.md, command file, and CLAUDE.md additions.
---

# /skill-creator — Build New Skills Fast

Takes a plain-language description of a task and generates a ready-to-use Claude Code skill: the SKILL.md instruction file, the command routing file, and the CLAUDE.md additions needed to wire it in.

## When to Use

- "I want a skill that does X"
- "Build me a slash command for Y"
- "Add a skill for [recurring task I do]"

## Instructions

### 1. Clarify the skill

Ask (or infer from context):
- **Name**: What should the slash command be called? (lowercase, hyphenated)
- **Trigger**: When should this skill activate?
- **Input**: What does the skill need to work? (files, user input, MCP data)
- **Output**: What does it produce? (files, terminal output, external actions)
- **Tools needed**: Which Claude Code tools will it use? (Read, Write, Edit, Bash, Glob, Grep, WebFetch, MCP tools)

### 2. Draft the SKILL.md

Create a skill file with this structure:

```markdown
---
name: [skill-name]
description: [One line, 60+ characters. Specific enough that Claude knows when to use it.]
---

# /[skill-name] — [Short Title]

[1-2 sentence overview of what this skill does and when to use it.]

## When to Use

- [Trigger condition 1]
- [Trigger condition 2]

## Instructions

### Step 1: [First action]
[Clear, specific instructions. Include exact commands, file paths, or tool calls.]

### Step 2: [Next action]
[Continue with sequential steps.]

### Step N: Output
[Define the expected output format.]

## Design Principles
- [Key principle 1]
- [Key principle 2]
```

**Quality checklist for the SKILL.md:**
- [ ] Frontmatter has `name` and `description` (description is 60+ chars)
- [ ] Instructions are step-by-step, not paragraph prose
- [ ] Each step names the specific tool or command to use
- [ ] Output format is defined (not left ambiguous)
- [ ] Any external state changes require user confirmation
- [ ] No hardcoded paths, IDs, or credentials — use config files or environment variables

### 3. Draft the command routing file

Create a short file for `.claude/commands/[name].md`:

```markdown
---
name: [skill-name]
description: [Same as SKILL.md description]
allowed-tools: [List of tools the skill needs]
---

Load and follow the instructions in `[path/to/SKILL.md]`.
```

### 4. Draft the CLAUDE.md additions

Two additions to propose:
1. A row in the slash command table (if one exists)
2. A routing rule in the "When to Load" section (if applicable)

### 5. Pre-ship checklist

- [ ] Skill file follows the standard structure
- [ ] Command routing file created
- [ ] CLAUDE.md updated with new command
- [ ] No hardcoded credentials, API keys, or personal paths
- [ ] External state changes (file writes, API calls, git operations) require confirmation
- [ ] Writing/content skills load a writing voice or style guide if available

### 6. Present for review

Show all artifacts. Ask: "Want me to save these, or make any changes first?"

## Tips for Good Skills

- **Be specific over flexible.** A skill that does one thing well beats one that tries to handle every edge case.
- **Include the output format.** If the skill produces a report, show exactly what the report looks like.
- **Gate destructive actions.** Anything that changes external state (git push, API calls, file deletes) should require explicit approval.
- **Reference, don't duplicate.** If a skill needs data from a file, read the file — don't copy its contents into the skill.
- **Keep it under 200 lines.** If a skill needs more, it's probably two skills.
