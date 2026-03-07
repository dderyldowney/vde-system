---
description: How to format git commit messages using Conventional Commits
---
# Git Commit Instructions

When making git commits, you MUST ALWAYS conform to the "Conventional Commits" standard (https://www.conventionalcommits.org/en/v1.0.0/#specification).

Your commit messages should be verbose, detailed, and clear. 

## Structure:
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]

## Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, etc)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools and libraries

## Details:
- The body MUST be verbose, explaining *what* was changed and *why*.
- Do not use one-line commit messages unless the change is extremely trivial.
- The description MUST be in the imperative, present tense ("change" not "changed" nor "changes").
