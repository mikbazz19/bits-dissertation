# Contributing to AI-Powered Resume Screening System

Thank you for your interest in contributing to this project! This document provides guidelines for contributions.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. If not, create a new issue with:
   - Clear, descriptive title
   - Detailed description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version)

### Suggesting Enhancements

1. Check if the enhancement has been suggested
2. Create an issue describing:
   - Clear use case
   - Proposed solution
   - Alternative approaches considered
   - Potential impact

### Code Contributions

#### Setup Development Environment

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/dissertation.git
   cd dissertation
   ```

3. Create virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov black flake8
   ```

5. Download spaCy model (optional but recommended):
   ```bash
   python -m spacy download en_core_web_sm
   ```

6. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### Coding Standards

- Follow PEP 8 style guide
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and concise
- Add comments for complex logic

#### Testing

- Write tests for new features
- Ensure all tests pass:
  ```bash
  pytest tests/ -v
  ```
- Maintain or improve code coverage

#### Code Formatting

Format your code before committing:
```bash
black src/ tests/
flake8 src/ tests/
```

#### Making Changes

1. Make your changes
2. Add/update tests
3. Run tests
4. Format code
5. Commit with clear message:
   ```bash
   git commit -m "Add feature: description of feature"
   ```

6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

7. Create Pull Request

### Pull Request Guidelines

- Provide clear description of changes
- Reference related issues
- Include test results
- Update documentation if needed
- Keep PRs focused on single feature/fix

## Code Review Process

1. Maintainers will review your PR
2. Address any feedback or requested changes
3. Once approved, PR will be merged

## Areas for Contribution

We welcome contributions in the following areas:

### High Priority

1. **Testing and Quality Assurance**
   - Expand test coverage
   - Add integration tests
   - Test with various resume formats
   - Email functionality testing

2. **Bug Fixes**
   - PDF parsing improvements
   - Skill extraction accuracy
   - Performance optimizations

3. **Documentation**
   - Code documentation
   - API documentation
   - Video tutorials
   - Example use cases

### Medium Priority

1. **New Features**
   - Bulk resume processing
   - Additional email providers
   - Export to PDF format
   - Dashboard analytics
   - Resume quality scoring

2. **UI/UX Improvements**
   - Mobile responsive design
   - Dark mode
   - Better visualizations
   - Progress indicators

3. **Machine Learning**
   - Improve skill matching algorithm
   - Semantic similarity using embeddings
   - Resume quality assessment
   - Job role classification

### Low Priority

1. **Integration**
   - ATS system integration
   - LinkedIn API integration
   - Cloud storage support

2. **Advanced Features**
   - Multi-language support
   - Custom reporting templates
   - Email analytics

## Recent Updates

### February 2026

- ✅ **Email Integration**: Multi-provider SMTP support with Gmail, Outlook, Yahoo
- ✅ **Connection Testing**: Test email configuration before sending
- ✅ **Enhanced Error Handling**: Better error messages and troubleshooting guides
- ✅ **Firewall Management**: Complete troubleshooting documentation

## Questions?

Feel free to open an issue for questions or clarifications.

Thank you for contributing!
