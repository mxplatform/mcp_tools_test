---
applyTo: '**'
---
Provide project context and coding guidelines that AI should follow when generating code, answering questions, or reviewing changes.

Assistant coding preferences:

- Always include docstrings and complete type annotations in any generated or modified code.
- Avoid adding inline comments inside code unless strictly necessary; prefer clear names and docstrings.
- When fixing an issue, attempt a minimal change-first approach and add small, focused tests when practical.
- Avoid long variable and function names where possible; prefer clear, concise identifiers.
- Do not add imports in the body of functions; place all imports at the top of the file.
- Always use 'uv run' before any command for running anything on terminal (pytest, scripts, etc).