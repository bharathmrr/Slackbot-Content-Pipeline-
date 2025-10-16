# CI/CD Pipeline Setup Guide

This document explains the comprehensive CI/CD pipeline implemented for the Slackbot Content Pipeline project.

## 🚀 Pipeline Overview

The CI/CD pipeline consists of multiple workflows that ensure code quality, security, and reliable deployments:

### Main Workflows

1. **CI/CD Pipeline** (`.github/workflows/ci-cd.yml`)
2. **Code Quality** (`.github/workflows/code-quality.yml`)
3. **Docker Security** (`.github/workflows/docker-security.yml`)
4. **Performance Testing** (`.github/workflows/performance-test.yml`)
5. **Dependency Updates** (`.github/workflows/dependency-update.yml`)

## 🔧 Required Secrets

Configure these secrets in your GitHub repository settings:

### Docker Hub
```
DOCKER_USERNAME=your-docker-username
DOCKER_PASSWORD=your-docker-password
```

### Render.com Deployment
```
RENDER_API_KEY=your-render-api-key
RENDER_STAGING_SERVICE_ID=your-staging-service-id
RENDER_PRODUCTION_SERVICE_ID=your-production-service-id
STAGING_URL=https://your-staging-app.onrender.com
PRODUCTION_URL=https://your-production-app.onrender.com
```

### Security Scanning
```
SNYK_TOKEN=your-snyk-token
SONAR_TOKEN=your-sonarcloud-token
```

### Notifications
```
SLACK_WEBHOOK=your-slack-webhook-url
```

## 📋 Workflow Details

### 1. Main CI/CD Pipeline

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main`
- Release publications

**Jobs:**
- **Test**: Multi-version Python testing (3.8-3.11)
- **Security**: Safety, Bandit, and Semgrep scans
- **Build**: Docker image build and push
- **Deploy Staging**: Auto-deploy to staging on `develop`
- **Deploy Production**: Auto-deploy to production on `main`
- **Release**: Automated release creation
- **Cleanup**: Artifact management

### 2. Code Quality Workflow

**Features:**
- Black code formatting
- isort import sorting
- flake8 linting
- mypy type checking
- Bandit security linting
- Radon complexity analysis
- SonarCloud integration

### 3. Docker Security Workflow

**Security Scans:**
- Trivy vulnerability scanner
- Docker Scout analysis
- Snyk container security
- Critical vulnerability blocking

### 4. Performance Testing

**Features:**
- Locust-based load testing
- Configurable test duration
- Performance report generation
- PR comments with results

### 5. Dependency Updates

**Automation:**
- Weekly dependency updates
- Security vulnerability checks
- Automated pull request creation
- Safety report generation

## 🏗️ Deployment Environments

### Staging Environment
- **Branch**: `develop`
- **URL**: Configured via `STAGING_URL` secret
- **Auto-deploy**: Yes
- **Tests**: Integration tests run post-deployment

### Production Environment
- **Branch**: `main`
- **URL**: Configured via `PRODUCTION_URL` secret
- **Auto-deploy**: Yes (with approval)
- **Tests**: Smoke tests run post-deployment

## 📊 Quality Gates

### Code Coverage
- Minimum: 80%
- Reports: HTML, XML, Terminal
- Fails build if below threshold

### Security
- Critical vulnerabilities block deployment
- High severity vulnerabilities generate warnings
- Security reports uploaded to GitHub Security tab

### Performance
- Response time monitoring
- Load testing on schedule
- Performance regression detection

## 🔄 Branch Strategy

```
main (production)
├── develop (staging)
├── feature/* (feature branches)
└── hotfix/* (emergency fixes)
```

### Workflow:
1. Create feature branch from `develop`
2. Submit PR to `develop` → triggers staging deployment
3. Merge to `develop` → auto-deploy to staging
4. Create PR from `develop` to `main` → triggers production deployment
5. Merge to `main` → auto-deploy to production

## 📝 Templates

### Pull Request Template
- Comprehensive checklist
- Security considerations
- Performance impact assessment
- Breaking changes documentation

### Issue Templates
- **Bug Report**: Structured bug reporting
- **Feature Request**: Feature specification template

## 🚨 Monitoring & Alerts

### Health Checks
- Endpoint: `/health`
- Frequency: Every 30 seconds
- Timeout: 30 seconds

### Notifications
- Slack notifications for deployments
- GitHub status checks
- Email alerts for critical issues

## 🛠️ Local Development

### Running Tests Locally
```bash
# Install test dependencies
pip install pytest pytest-cov pytest-asyncio

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test types
pytest -m unit
pytest -m integration
```

### Code Quality Checks
```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Lint code
flake8 app/ tests/

# Type check
mypy app/

# Security scan
bandit -r app/
```

### Docker Testing
```bash
# Build image
docker build -t slackbot-pipeline .

# Run security scan
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image slackbot-pipeline

# Run container
docker run -p 8000:8000 --env-file .env slackbot-pipeline
```

## 🔧 Configuration Files

### pytest.ini
- Test configuration
- Coverage settings
- Marker definitions

### sonar-project.properties
- SonarCloud configuration
- Quality gate settings
- Coverage exclusions

### render.yaml
- Render.com deployment config
- Environment variables
- Health check settings

## 📈 Metrics & Reporting

### Code Quality Metrics
- **Coverage**: Minimum 80%
- **Complexity**: Monitored via Radon
- **Maintainability**: SonarCloud metrics
- **Security**: Vulnerability count tracking

### Performance Metrics
- **Response Time**: < 5 seconds
- **Throughput**: Load testing results
- **Availability**: Health check monitoring

### Deployment Metrics
- **Success Rate**: Deployment success tracking
- **Rollback Time**: Recovery metrics
- **Lead Time**: Feature delivery speed

## 🚀 Getting Started

1. **Fork the repository**
2. **Configure secrets** in GitHub settings
3. **Set up environments** (staging, production)
4. **Configure Render.com** services
5. **Test the pipeline** with a small change

The pipeline will automatically trigger on your first push to `main` or `develop`!

## 🆘 Troubleshooting

### Common Issues

**Build Failures:**
- Check Python version compatibility
- Verify dependency versions
- Review test failures

**Deployment Issues:**
- Verify Render.com secrets
- Check environment variables
- Review health check endpoints

**Security Scan Failures:**
- Update vulnerable dependencies
- Review security scan reports
- Apply security patches

### Support
- Check GitHub Actions logs
- Review deployment logs in Render.com
- Monitor application logs via health endpoints
