---
description: How to format git commit messages using Conventional Commits
---
# Git Commit Instructions

When making git commits, you MUST ALWAYS conform to the "Conventional Commits" standard (v1.0.0).

Your commit messages should be verbose, detailed, and clear. 

## Structure:
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Specification Rules:
1. Commits MUST be prefixed with a type, which consists of a noun (feat, fix, etc.), followed by the OPTIONAL scope, OPTIONAL `!`, and REQUIRED terminal colon and space.
2. The type `feat` MUST be used when a commit adds a new feature.
3. The type `fix` MUST be used when a commit represents a bug fix.
4. A scope MAY be provided after a type. A scope MUST consist of a noun describing a section of the codebase surrounded by parenthesis, e.g., `fix(parser):`
5. A description MUST immediately follow the colon and space. The description is a short summary of the code changes.
6. A longer commit body MAY be provided after the short description, providing additional contextual information about the code changes. The body MUST begin one blank line after the description.
7. A commit body is free-form and MAY consist of any number of newline separated paragraphs.
8. One or more footers MAY be provided one blank line after the body. Each footer MUST consist of a word token, followed by either a `:<space>` or `<space>#` separator, followed by a string value.
9. A footer’s token MUST use `-` in place of whitespace characters, e.g., `Acked-by`. An exception is made for `BREAKING CHANGE`, which MAY also be used as a token.
10. Breaking changes MUST be indicated in the type/scope prefix of a commit (by a `!` before the colon), or as an entry in the footer starting with `BREAKING CHANGE:`.
11. Types other than `feat` and `fix` MAY be used in your commit messages, e.g., `docs:`, `chore:`, `refactor:`, `test:`, `style:`, `perf:`, etc.
12. The description MUST be in the imperative, present tense ("change" not "changed" nor "changes").

## Examples:

**Commit message with detailed body and multiple footers**
```
fix: prevent racing of requests 

Introduce a request id and a reference to latest request. Dismiss incoming responses other than from latest request. Remove timeouts which were used to mitigate the racing issue but are obsolete now. 

Reviewed-by: Z 
Refs: #123
```

**Commit message with scope and breaking change marker (`!`)**
```
feat(api)!: send an email to the customer when a product is shipped
```

**Commit message with both `!` and BREAKING CHANGE footer**
```
chore!: drop support for Node 6 

BREAKING CHANGE: use JavaScript features not available in Node 6.
```

**Commit message with no body** (Only for trivial changes)
```
docs: correct spelling of CHANGELOG
```
