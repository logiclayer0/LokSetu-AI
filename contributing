# Contributing to LokSetu AI

First off, thank you for considering contributing to LokSetu AI. It is people like you that make open-source such a powerful tool for innovation and public good.

This document provides guidelines and instructions for contributing to this project.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Branching Strategy](#branching-strategy)
- [Commit Message Convention](#commit-message-convention)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)
- [Recognition](#recognition)
- [Questions](#questions)

---

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

### Our Standards

| Behavior | Expected |
|----------|----------|
| Respect | Treat everyone with respect and kindness |
| Inclusivity | Welcome newcomers and beginners |
| Feedback | Provide constructive criticism |
| Focus | Prioritize what is best for the community |
| Empathy | Show empathy towards other members |

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling, insulting, or derogatory remarks
- Public or private harassment
- Publishing others' private information without consent

---

## How Can I Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce the issue**
- **Expected vs actual behavior**
- **Screenshots or code snippets if applicable**
- **Environment details** (OS, Python version, Node version, browser)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title and description**
- **Use case and motivation**
- **Possible implementation approach**
- **Alternative solutions considered**

### Your First Code Contribution

Unsure where to begin? Look for issues labeled:

| Label | Meaning |
|-------|---------|
| `good first issue` | Simple issues for newcomers |
| `help wanted` | Issues needing community help |
| `documentation` | Documentation improvements |

---

## Development Setup

### Step 1 — Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/loksetu-ai.git
cd loksetu-ai
```

### Step 2 — Add Upstream Remote

```bash
git remote add upstream https://github.com/ORIGINAL_OWNER/loksetu-ai.git
git remote -v
```

### Step 3 — Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4 — Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### Step 5 — Verify Setup

| Service | URL | Expected |
|---------|-----|----------|
| Backend | http://localhost:8000 | JSON response |
| Swagger | http://localhost:8000/docs | API docs |
| Frontend | http://localhost:5173 | Login page |

---

## Branching Strategy

We follow a simplified Git Flow workflow.

### Branch Types

| Branch | Purpose | Example |
|--------|---------|---------|
| `main` | Production-ready code | — |
| `develop` | Integration branch | — |
| `feature/*` | New features | `feature/voice-complaints` |
| `bugfix/*` | Bug fixes | `bugfix/cors-error` |
| `hotfix/*` | Urgent production fixes | `hotfix/auth-bypass` |
| `docs/*` | Documentation | `docs/api-reference` |
| `refactor/*` | Code refactoring | `refactor/ai-service` |

### Workflow

```bash
git checkout main
git pull upstream main

git checkout -b feature/your-feature-name

git add .
git commit -m "feat: add your feature"

git push origin feature/your-feature-name
```

---

## Commit Message Convention

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format

```text
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

| Type | Purpose |
|------|---------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Code style (formatting, no logic change) |
| `refactor` | Code refactoring |
| `perf` | Performance improvement |
| `test` | Adding or updating tests |
| `chore` | Build process, dependencies |
| `ci` | CI/CD configuration |
| `revert` | Reverting a commit |

### Scope Examples

| Scope | Area |
|-------|------|
| `auth` | Authentication |
| `complaints` | Complaint management |
| `analytics` | Analytics module |
| `policy` | Policy simulator |
| `admin` | Admin panel |
| `ui` | User interface |
| `api` | API endpoints |
| `db` | Database |

### Examples

```bash
feat(auth): add role-based login verification
fix(complaints): resolve duplicate complaint submission
docs(readme): update deployment instructions
refactor(ai-service): simplify Groq API error handling
test(analytics): add unit tests for hotspot detection
```

---

## Pull Request Process

### Before Submitting

| Step | Action |
|------|--------|
| 1 | Sync with upstream main |
| 2 | Run backend tests — `pytest` |
| 3 | Run frontend lint — `npm run lint` |
| 4 | Update documentation if needed |
| 5 | Squash commits if too many |

### Sync with Upstream

```bash
git checkout main
git pull upstream main
git checkout your-branch
git rebase main
```

### Submitting

1. Push your branch to your fork
2. Open a Pull Request against `main`
3. Fill in the PR template completely
4. Link related issues using `Closes #123` or `Fixes #123`

### PR Title Format

```text
<type>(<scope>): <short description>
```

Example: `feat(auth): add role-based login verification`

### PR Description Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #123

## Testing
Describe how you tested your changes.

## Screenshots
If applicable, add screenshots.

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] No merge conflicts
```

### Review Process

| Step | Description |
|------|-------------|
| 1 | Maintainers review within 3-5 days |
| 2 | Address all review comments |
| 3 | Request re-review after changes |
| 4 | Once approved, maintainer merges |

---

## Coding Standards

### Python (Backend)

| Rule | Tool |
|------|------|
| PEP 8 compliance | Base standard |
| Formatting | Black (line length 88) |
| Import sorting | isort |
| Linting | flake8 |
| Type hints | Required for all signatures |

```python
async def create_complaint(complaint: ComplaintCreate) -> ComplaintResponse:
    """Create a new complaint and categorize it using AI."""
    ...
```

### JavaScript / React (Frontend)

| Rule | Description |
|------|-------------|
| Linting | ESLint with React plugin |
| Formatting | Prettier |
| Components | Functional with hooks |
| Exports | Named exports |
| Naming | Descriptive variable names |

```jsx
const ComplaintCard = ({ complaint, onClick }) => {
  return (
    <div onClick={() => onClick?.(complaint)}>
      ...
    </div>
  )
}
```

### General Guidelines

- Write self-documenting code
- Keep functions small and focused
- Avoid deep nesting (max 3 levels)
- Use meaningful names
- Comment only when necessary
- No commented-out code in PRs

---

## Testing Guidelines

### Backend Tests

```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=app --cov-report=html
```

### Writing Tests

| Rule | Description |
|------|-------------|
| File naming | `test_<module>.py` |
| Function naming | `test_<feature>_<scenario>` |
| Fixtures | Use for common setup |
| Mocks | Mock external services (Groq API) |

```python
def test_register_user_success(client):
    response = client.post("/api/v1/auth/register", json={
        "full_name": "Test User",
        "email": "test@example.com",
        "password": "test1234",
        "role": "citizen"
    })
    assert response.status_code == 201
```

### Frontend Tests

- Use React Testing Library
- Test user interactions
- Avoid testing implementation details

---

## Documentation

### Code Documentation

| Type | Requirement |
|------|-------------|
| Docstrings | All public functions |
| JSDoc | Complex JavaScript functions |
| Inline comments | Non-obvious logic only |
| Type hints | All Python functions |

### Project Documentation

Located in `docs/`:

| File | Purpose |
|------|---------|
| `architecture.md` | System architecture |
| `api_docs.md` | API reference |
| `demo_script.md` | Demo walkthrough |

Update docs when:

- Adding new features
- Changing API endpoints
- Modifying architecture
- Adding dependencies

---

## Reporting Bugs

### Before Reporting

1. Check if bug is already reported
2. Try to reproduce in latest version
3. Gather environment info
4. Prepare minimal reproduction

### Bug Report Template

```markdown
**Describe the bug**
Clear description of the bug.

**To Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable.

**Environment:**
- OS: [e.g., Windows 11]
- Browser: [e.g., Chrome 120]
- Python: [e.g., 3.11.5]
- Node: [e.g., 20.10.0]

**Additional context**
Any other relevant information.
```

---

## Suggesting Enhancements

### Enhancement Template

```markdown
**Is your feature request related to a problem?**
Clear description of the problem.

**Describe the solution you'd like**
Clear description of what you want.

**Describe alternatives considered**
Any alternative solutions.

**Additional context**
Screenshots, mockups, or examples.
```

---

## Recognition

Contributors will be:

| Recognition | Location |
|-------------|----------|
| Listed in contributors file | `CONTRIBUTORS.md` |
| Mentioned in release notes | GitHub Releases |
| Credited in documentation | Relevant docs |

---

## Questions

| Channel | Link |
|---------|------|
| GitHub Discussions | [Open a discussion](https://github.com/your-username/loksetu-ai/discussions) |
| Email | contact@loksetu.ai |
| Tag maintainers | `@maintainer-username` |

---

<div align="center">

**Thank you for contributing to LokSetu AI**

*Together, we build a better bridge between citizens and policymakers.*

</div>
