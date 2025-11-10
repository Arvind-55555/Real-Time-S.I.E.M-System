# Contributing to SIEM Analysis Platform

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🤝 How to Contribute

### Reporting Bugs

1. **Check existing issues** to avoid duplicates
2. **Use the bug report template** when creating a new issue
3. **Provide detailed information**:
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, browser, versions)
   - Screenshots if applicable

### Suggesting Features

1. **Check the roadmap** to see if it's already planned
2. **Open a feature request** with:
   - Clear description of the feature
   - Use case and benefits
   - Potential implementation approach

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**
   - Follow the coding standards
   - Add tests for new functionality
   - Update documentation as needed

4. **Commit your changes**
   ```bash
   git commit -m 'Add some amazing feature'
   ```
   Follow [Conventional Commits](https://www.conventionalcommits.org/)

5. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

6. **Open a Pull Request**
   - Provide a clear description
   - Reference related issues
   - Ensure all tests pass

## 📝 Coding Standards

### JavaScript/React

- Use ES6+ features
- Follow Airbnb JavaScript Style Guide
- Use functional components with hooks
- Keep components under 300 lines
- Write descriptive variable names

```javascript
// Good
const calculateThreatScore = (requests, failures) => {
  return (failures / requests) * 100;
};

// Bad
const calc = (r, f) => {
  return (f / r) * 100;
};
```

### Python

- Follow PEP 8 style guide
- Use type hints where applicable
- Write docstrings for functions/classes
- Keep functions focused and small

```python
# Good
def detect_anomalies(ip_stats: dict, threshold: int = 30) -> list:
    """
    Detect anomalous IP behavior based on statistical analysis.
    
    Args:
        ip_stats: Dictionary of IP statistics
        threshold: Minimum anomaly score to flag (default: 30)
        
    Returns:
        List of anomalous IPs with scores
    """
    pass

# Bad
def detect(stats, t=30):
    pass
```

## 🧪 Testing

### Running Tests

```bash
# JavaScript tests
npm test

# Python tests
pytest tests/

# Coverage report
npm run test:coverage
pytest --cov=scripts tests/
```

### Writing Tests

- Write unit tests for new functions
- Include edge cases
- Test both success and failure scenarios
- Aim for >80% code coverage

## 📚 Documentation

- Update README.md for new features
- Add inline comments for complex logic
- Update API documentation
- Include examples where helpful

## 🔍 Code Review Process

1. All PRs require at least one approval
2. CI/CD checks must pass
3. Code must follow style guidelines
4. Documentation must be updated
5. Tests must pass with adequate coverage

## 🎯 Priority Areas

We're especially interested in contributions for:

- 🔐 **Security enhancements**
- 🤖 **Machine learning models**
- 🌍 **GeoIP integration**
- 📊 **Advanced visualizations**
- 🔔 **Alerting systems**
- 🗄️ **Database integrations**

## 💬 Communication

- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: General questions and ideas
- **Pull Requests**: Code contributions

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for making the SIEM Analysis Platform better!