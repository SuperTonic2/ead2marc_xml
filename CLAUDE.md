# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

<!-- Ask Claude to analyze the codebase and fill in this section -->

## Key References

- `PROJECT_BRIEF.md` - Detailed architecture and requirements
- `README.md` - Repository layout and contribution rules
- `tasks/todo.md` - Current task tracking

## Development Workflow

1. **First think through the problem, read the codebase for relevant files, and write a plan to `tasks/todo.md`.**

2. **The plan should have a list of todo items that you can check off as you complete them.**

3. **Before you begin working, check in with me and I will verify the plan.**

4. **Then, begin working on the todo items, marking them as complete as you go.**

5. **Please every step of the way just give me a high level explanation of what changes you made.**

6. **Make every task and code change as simple as possible.**  
   We want to avoid making any massive or complex changes.  
   Every change should impact as little code as possible.  
   Everything is about *simplicity*.

7. **Finally, add a review section to the `todo.md` file with a summary of the changes you made and any other relevant information.**

8. **DO NOT BE LAZY. NEVER BE LAZY. IF THERE IS A BUG FIND THE ROOT CAUSE AND FIX IT. NO TEMPORARY FIXES. YOU ARE A SENIOR DEVELOPER. NEVER BE LAZY.**

9. **MAKE ALL FIXES AND CODE CHANGES AS SIMPLE AS HUMANLY POSSIBLE.**
   They should only impact necessary code relevant to the task and nothing else.
   It should impact as little code as possible.
   Your goal is to **not introduce any bugs**.
   *It's all about simplicity.*

## Common Commands

```bash
npm run dev          # Start dev server
npm run build        # Production build
npm run lint         # Run linter
npm test             # Run tests
```

## Architecture Notes

<!-- Add project-specific architecture info here -->
