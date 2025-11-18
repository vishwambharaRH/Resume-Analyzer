# CI/CD Pipeline Documentation & Reliability

Our project uses **GitHub Actions** to provide a complete CI/CD workflow for automated testing, quality checks, security scanning, and deployment packaging.

The pipeline runs automatically on:

- **Every push** to `main` or `develop`
- **Every pull request** targeting `main` or `develop`
- **Manual dispatch via GitHub Actions**

---

## CI/CD Pipeline Overview

The CI/CD workflow is divided into **six major stages**, each with strict quality gates and automated validation steps.

---

## 1. Build Stage

**Purpose:**  
Prepare and build both backend and frontend code.

**Key Steps:**
- Checkout the repository
- Install Python 3.10 + backend dependencies
- Install Node.js 20 + frontend dependencies
- Build frontend (Vite/React)
- Upload build output as artifact (`frontend-build`)

**Tools Used:**  
Python, pip, Node.js, npm

---

## 2. Test Stage (Unit, Integration, System)

**Purpose:**  
Ensure application correctness with automated testing.

**Actions Performed:**
- Execute backend tests using `pytest`
- Run unit, integration, and system tests
- Enforce minimum coverage of **75%**
- Test frontend (if tests exist under `/frontend/__tests__/`)
- Validate Grammar Engine & Action Verb Engine

**Tools Used:**
- `pytest`, `pytest-cov`, `pytest-html`
- `spacy`
- `npm test`

**Quality Gates:**
- ✔ All tests must pass  
- ✔ Test coverage ≥ **75%**

---

## 3. Coverage Stage

**Purpose:**  
Generate complete code coverage reports.

**Actions Performed:**
- Run pytest with branch coverage
- Generate HTML coverage folder (`htmlcov/`)
- Fail pipeline if coverage < **75%**

**Tool:** `pytest-cov`

---

## 4. Lint Stage (Static Analysis)

Ensures consistent coding style and readability.

### Python Lint:
- Runs `pylint` on `/src/`
- Extracts score automatically
- Enforces minimum score of **7.5/10**

### JavaScript Lint:
- Installs and runs ESLint through `npm run lint`

**Quality Gates:**
- ✔ Python lint score ≥ **7.5/10**
- ✔ No ESLint errors

---

## 5. Security Scan Stage

**Purpose:**  
Detect vulnerabilities in source code and dependencies.

### Bandit:
- Static code analysis using:
```
bandit -r src -f json
```
- Pipeline fails if:
- HIGH severity issues OR
- HIGH confidence vulnerabilities are present

### Safety:
- Dependency vulnerability scan (CVEs)
- Full report saved to `safety-report.txt`

**Reports generated:**
- `bandit-report.json`
- `safety-report.txt`

---

## 6. Deployment Artifact Stage

**Runs only on:**  
✔ Push to `main`  
✔ After ALL previous stages pass successfully  

**Purpose:**  
Package the fully validated project along with all reports.

### Artifact Includes:

#### 1. Source Code
- `src/`
- `frontend/dist/` (fully built frontend)

#### 2. Reports
- `htmlcov/` (coverage report)
- `pylint-report.txt`
- `pytest-report.html`
- `test-results.xml`
- `bandit-report.json`
- `safety-report.txt`

#### 3. Required Project Files
- `README.md`
- `requirements.txt`
- `frontend/package.json`

#### 4. Packaging
The artifact is created with a date-stamped filename:

deployment-package-YYYYMMDD.zip

---

# Quality Gates Summary

| Check | Requirement | Enforced |
|------|-------------|----------|
| Python Lint Score | ≥ 7.5/10 | ✔ Yes |
| Test Coverage | ≥ 75% | ✔ Yes |
| Security Scan | No HIGH severity issues | ✔ Yes |
| All Tests Pass | Required | ✔ Yes |
| Frontend Build Passes | Required | ✔ Yes |

---

# Running CI Pipeline Locally

## Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/ -v

# Check coverage
pytest --cov=src --cov-report=html

# Linting
pylint src/

# Security scanning
bandit -r src/
safety check
```