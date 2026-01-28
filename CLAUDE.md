# Ashlag Yomi - Claude Code Project Instructions

## Project Overview
This project uses Claude Code for development with the Ralph Wiggum iterative development technique.

## Development Workflow

### Using Ralph Wiggum Loop
For iterative development tasks, use the ralph.sh script:

```bash
# Basic usage
./ralph.sh "Your task description. Output COMPLETE when done." --max-iterations 20

# Using a prompt file
./ralph.sh --prompt-file prompts/feature.md --max-iterations 30 --verbose

# With specific model
./ralph.sh --model opus "Complex task here. Output COMPLETE when done."
```

### Key Principles
1. **Clear completion criteria**: Always specify exactly when a task is done
2. 2. **Incremental goals**: Break large tasks into phases
   3. 3. **Self-correction**: Include test/verify steps in prompts
      4. 4. **Safety nets**: Always use --max-iterations
        
         5. ## Project Structure
         6. ```
            ashlag-yomi/
            ├── CLAUDE.md          # This file - Claude Code instructions
            ├── ralph.sh           # Ralph Wiggum loop script
            ├── prompts/           # Prompt templates for common tasks
            │   ├── feature.md
            │   ├── bugfix.md
            │   └── refactor.md
            └── src/               # Source code (to be created)
            ```

            ## Coding Standards
            - Use TypeScript for type safety
            - - Write tests for all new features
              - - Follow existing code patterns
                - - Document public APIs
                 
                  - ## Commands Reference
                  - - `./ralph.sh --help` - Show all options
                    - - `./ralph.sh --dry-run "task"` - Preview without executing
                     
                      - ## Completion Signals
                      - When working on tasks, output one of:
                      - - `<promise>COMPLETE</promise>` - Task finished successfully
                        - - `<promise>BLOCKED</promise>` - Cannot proceed, needs human input
