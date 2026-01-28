# ashlag-yomi

Daily learning project using Claude Code with the Ralph Wiggum AI loop technique.

## Quick Start

```bash
# Clone the repo
git clone https://github.com/naorbrown/ashlag-yomi.git
cd ashlag-yomi

# Make ralph.sh executable
chmod +x ralph.sh

# Run your first loop
./ralph.sh "Build a hello world API. Output COMPLETE when done." --max-iterations 10
```

## Project Structure

```
ashlag-yomi/
├── CLAUDE.md      # Claude Code project instructions
├── ralph.sh       # Ralph Wiggum loop script
├── prompts/       # Prompt templates
│   ├── feature.md
│   └── bugfix.md
└── README.md
```

## Using Ralph Wiggum

Ralph Wiggum is an iterative AI development technique that repeatedly feeds a prompt to Claude until completion.

### Basic Usage

```bash
# Direct prompt
./ralph.sh "Your task. Output COMPLETE when done." --max-iterations 20

# Using a prompt file
./ralph.sh --prompt-file prompts/feature.md --max-iterations 30 --verbose
```

### Options

- `--max-iterations N` - Safety limit (default: 50)
- - `--completion-promise STR` - Completion signal (default: COMPLETE)
  - - `--prompt-file FILE` - Use markdown file as prompt
    - - `--verbose` - Show iteration progress
      - - `--dry-run` - Preview without executing
       
        - ## Resources
       
        - - [Ralph Wiggum Guide](https://awesomeclaude.ai/ralph-wiggum)
          - - [Claude Code Docs](https://docs.anthropic.com/claude-code)
