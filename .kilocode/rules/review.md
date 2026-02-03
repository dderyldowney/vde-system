---
description: Rules for performing local code reviews focusing on quality and security.
globs: ["**/*"]
---

# Code Review Protocol

When performing a review in this project, adhere to the following standards:

## 1. Security First
- Flag any hardcoded secrets, API keys, or credentials.
- Identify potential SQL injection, XSS, or insecure data handling.
- Ensure input validation is present for all public-facing methods.

## 2. Performance & Logic
- Check for inefficient loops or unnecessary database queries.
- Identify potential race conditions in asynchronous code.
- Ensure edge cases (null values, empty arrays) are handled.

## 3. Maintainability
- Verify that complex logic is documented or simplified.
- Check that variable and function names follow the project's style.
- Ensure the code does not violate DRY (Don't Repeat Yourself) principles.

## 4. Response Format
- Provide a summary of the most critical issues first.
- Use inline code snippets to show suggested refactors.
- Categorize feedback as: **[Critical]**, **[Major]**, or **[Minor/Nit]**.

