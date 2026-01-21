# Contributing to VDE

Thank you for your interest in contributing to the VDE (Virtual Development Environment) project!

## Table of Contents
- [Quick Start](#quick-start)
- [Ways to Contribute](#ways-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)
- [Documentation](#documentation)
- [Community Guidelines](#community-guidelines)

## Quick Start

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/vde-system.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Run tests: `make check`
6. Commit and push: `git push origin feature/your-feature-name`
7. Open a Pull Request

See [Development Setup](#development-setup) for detailed instructions.

## Ways to Contribute

We welcome contributions in many forms beyond just code!

### Code Contributions
- **Bug fixes**: See [Reporting Issues](#reporting-issues)
- **New features**: Start with an issue or discussion first
- **Refactoring**: Improve code structure while maintaining functionality
- **Performance improvements**: Optimize existing code
- **Tests**: Add test coverage for existing or new functionality
- **Documentation**: Improve code comments and docstrings

### Documentation Contributions
- **Fix typos**: Spelling, grammar, clarity
- **Add examples**: Usage examples, tutorials, recipes
- **Improve guides**: Make them clearer, more comprehensive
- **Translate**: Add translations for international users
- **Update README**: Keep project description current

### Testing & Quality
- **Report bugs**: Detailed bug reports with reproduction steps
- **Test on different platforms**: macOS, Linux, different Docker versions
- **Add test cases**: Cover edge cases, error conditions
- **Performance testing**: Identify bottlenecks
- **Security auditing**: Find and report vulnerabilities

### Community & Support
- **Answer questions**: Help other users on issues and discussions
- **Write tutorials**: Blog posts, videos, guides
- **Share your use cases**: How you use VDE in your workflow
- **Review PRs**: Provide constructive feedback on pull requests
- **Triaging issues**: Help classify and prioritize incoming issues

### Design & Feedback
- **UI/UX suggestions**: Improve command-line interface
- **Feature requests**: Well-thought-out proposals
- **Architecture discussions**: Design patterns, project structure
- **Accessibility**: Make VDE more accessible to all users

## Development Setup

### Prerequisites
- **zsh** (5.0+): All scripts use zsh
- **Docker** (20.10+): For testing and development
- **jq** (1.5+): JSON processing
- **kcov** (40+): Code coverage (optional)

See [TESTING.md](docs/TESTING.md) for detailed installation instructions.

### Initial Setup
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/vde-system.git
cd vde-system

# Install dependencies (see TESTING.md)
make install-deps

# Verify setup
zsh --version
docker --version
```

### Creating a Development Environment

```bash
# List available VMs
./scripts/vde list

# Create and start a test VM
./scripts/vde create python
./scripts/vde start python

# Connect to the VM
ssh python-dev
```

## Coding Standards

**All contributions must follow the project's coding standards.**

Please read:
- **[STYLE_GUIDE.md](STYLE_GUIDE.md)**: Comprehensive zsh coding standards
- **[TESTING.md](docs/TESTING.md)**: Testing guidelines and CI/CD pipeline

### Key Points
- Use zsh (not bash/sh)
- Follow naming conventions
- Always quote variables
- Add error handling
- Write tests for new features
- Update documentation

### Quick Reference
```bash
# Check syntax
zsh -n your-script.sh

# Run tests
make test

# Run linting
make lint

# Run all checks
make check
```

## Testing

### Before Submitting
```bash
# Run full test suite
make check

# This runs:
# - make lint      (zsh syntax check, yamllint)
# - make test       (all tests)
```

### Test Categories
1. **Unit tests**: Test individual functions and libraries
2. **Integration tests**: Test component interactions
3. **Comprehensive tests**: Extended test suites
4. **Coverage tests**: Verify code coverage levels

See [TESTING.md](docs/TESTING.md) for details.

### Writing Tests
- Add tests for new functionality
- Follow existing test patterns in `tests/unit/` and `tests/integration/`
- Use `tests/lib/test_common.sh` utilities
- Ensure tests are fast and reliable

```zsh
#!/usr/bin/env zsh
# Test example
TEST_DIR="$(cd "$(dirname "${(%):-%x}")/../.." && pwd)"
source "$TEST_DIR/tests/lib/test_common.sh"

test_suite_start "My Feature Tests"

setup_test_env

# Your tests here
test_section "Basic functionality"
assert_equals "expected" "actual" "description"

teardown_test_env

test_suite_end "My Feature Tests"
```

## Submitting Changes

### Commit Messages
Use clear, descriptive commit messages:

```
feat: Add support for Rust development environment

- Add rust-dev VM with cargo and rustup
- Configure SSH access on port 2206
- Add comprehensive tests

Fixes #123
Co-Authored-By: Your Name <your.email@example.com>
```

Commit message prefixes:
- `feat:`: New feature
- `fix:`: Bug fix
- `docs:`: Documentation changes
- `test:`: Adding or updating tests
- `refactor:`: Code refactoring
- `style:`: Code style changes (formatting, etc.)
- `perf:`: Performance improvements
- `ci:`: CI/CD changes

### Pull Request Process
1. **Keep PRs focused**: One feature or fix per PR
2. **Update documentation**: Include doc changes in the PR
3. **Add tests**: Ensure tests pass locally
4. **Describe changes**: Explain what and why in PR description
5. **Link issues**: Reference related issues with `Fixes #123` or `Relates to #123`
6. **Respond to feedback**: Address review comments promptly

### PR Description Template
```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests pass locally
- [ ] Manual testing completed

## Checklist
- [ ] Code follows STYLE_GUIDE.md
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Commit message follows conventions
```

## Reporting Issues

### Before Reporting
1. **Search existing issues**: Check if your issue has already been reported
2. **Check recent commits**: Your issue may already be fixed
3. **Try the latest version**: Ensure you're using the latest release

### Bug Reports
Good bug reports help us fix issues faster:

**Title**: Clear, concise description

**Body**:
```markdown
## Description
What happened and what should happen

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should have happened

## Actual Behavior
What actually happened (include error messages)

## Environment
- OS: macOS 14.0
- Docker version: 24.0.0
- VDE version: main branch (commit abc123)

## Additional Context
Screenshots, logs, or other helpful information
```

### Feature Requests
We welcome feature requests! Help us understand your need:

```markdown
## Problem Description
What problem are you trying to solve?

## Proposed Solution
How do you envision this feature working?

## Alternatives Considered
What other approaches did you consider?

## Additional Context
Examples, use cases, or supporting information
```

## Documentation

### Types of Documentation
- **README.md**: Project overview and quick start
- **docs/**: Detailed guides (TESTING.md, COVERAGE.md, etc.)
- **Code comments**: Inline documentation for complex logic
- **Man pages**: Command help (`vde --help`)

### Improving Documentation
1. **Be clear**: Write for your audience
2. **Be concise**: Get to the point
3. **Include examples**: Show, don't just tell
4. **Keep it current**: Update docs when code changes
5. **Use consistent formatting**: Follow existing patterns

### Documentation Areas
- **User guides**: How to use VDE features
- **Developer guides**: How to extend VDE
- **API docs**: For library interfaces
- **Architecture docs**: System design and patterns
- **Troubleshooting**: Common issues and solutions

## Community Guidelines

### Our Pledge
- **Inclusive**: Welcome contributors from all backgrounds
- **Respectful**: Treat others with dignity and respect
- **Collaborative**: Work together constructively
- **Supportive**: Help others learn and grow

### Expected Behavior
- **Be patient**: Not everyone has the same background or experience level
- **Be constructive**: Critique ideas, not people
- **Be professional**: Keep discussions focused and productive
- **Be inclusive**: Use inclusive language and welcome diverse perspectives

### Unacceptable Behavior
- Harassment or discriminatory language
- Personal attacks or insults
- Spam or self-promotion without adding value
- Trolling or disruptive behavior

### Getting Help
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Pull Requests**: Code contributions and reviews

### Conflict Resolution
If you encounter issues:
1. **Try to resolve directly**: Communicate respectfully
2. **Escalate if needed**: Contact maintainers privately
3. **Be willing to compromise**: Find solutions that work for everyone

## Recognition

Contributors are recognized in:
- **CONTRIBUTORS.md**: List of all contributors
- **Release notes**: Notable contributions in each release
- **Commit messages**: Co-Authored-By for significant contributions

## Getting Started

### Good First Issues
Look for issues labeled:
- `good first issue`: Suitable for newcomers
- `help wanted`: Community contributions welcome
- `documentation`: Docs improvements needed

### Questions?
- **Check existing docs**: README.md, TESTING.md, STYLE_GUIDE.md
- **Search issues**: Your question may have been answered
- **Open an issue**: Ask on GitHub Issues or Discussions

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

---

**Thank you for contributing to VDE!** 🚀

Every contribution helps make VDE better, whether it's code, documentation, testing, or helping other users.
