# Jobéco Application - Test Suite

This directory contains comprehensive tests for the Jobéco application, covering all major services and functionality.

## Test Files

- `test_app.py` - Main test suite with all test cases
- `run_tests.py` - Test runner with command-line options
- `TEST_README.md` - This documentation file

## Running Tests

### Basic Usage

```bash
# Run all tests
python test_app.py

# Or use the test runner
python run_tests.py
```

### Advanced Usage

```bash
# Run tests for a specific service
python run_tests.py --service database
python run_tests.py --service user
python run_tests.py --service group
python run_tests.py --service tradesman
python run_tests.py --service job
python run_tests.py --service integration

# Run only basic tests (skip integration tests)
python run_tests.py --quick

# Verbose output
python run_tests.py --verbose

# Combine options
python run_tests.py --service user --verbose
```

## Test Coverage

### Database Service Tests (`TestDatabaseService`)
- Database initialization
- Query execution
- Single query execution
- Insert operations

### User Service Tests (`TestUserService`)
- User creation
- User retrieval by ID and username
- Password verification
- User authentication

### Group Service Tests (`TestGroupService`)
- Group creation
- Group retrieval
- User-group membership management
- Group member listing

### Tradesman Service Tests (`TestTradesmanService`)
- Tradesman creation
- Tradesman retrieval
- User-tradesman relationships
- Tradesman management

### Job Service Tests (`TestJobService`)
- Job creation
- Quote creation
- Job/quote retrieval
- Job status management

### Integration Tests (`TestIntegration`)
- Complete workflow testing
- User â†’ Group â†’ Tradesman â†’ Job relationships
- Cross-service functionality

## Test Features

### Isolated Testing
- Each test uses a temporary database
- Tests are independent and don't affect each other
- Automatic cleanup after each test

### Comprehensive Coverage
- Tests all major service methods
- Validates data integrity
- Tests error conditions
- Verifies relationships between entities

### Realistic Data
- Uses realistic test data
- Tests actual business workflows
- Validates constraints and relationships

## Test Output

The test runner provides detailed output including:

```
Running Jobéco Application Tests...
==================================================
test_database_initialization (__main__.TestDatabaseService) ... ok
test_execute_query (__main__.TestDatabaseService) ... ok
test_execute_single_query (__main__.TestDatabaseService) ... ok
test_execute_insert (__main__.TestDatabaseService) ... ok
...

==================================================
Test Summary:
Tests run: 25
Failures: 0
Errors: 0
Success rate: 100.0%
==================================================

âœ… All tests passed!
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're running tests from the project root directory
2. **Database Errors**: Tests create temporary databases, so ensure write permissions
3. **Service Errors**: Verify all service files are present in `app/services/`

### Debug Mode

For debugging test failures, run with verbose output:

```bash
python run_tests.py --verbose
```

This will show detailed information about each test case.

## Adding New Tests

To add new tests:

1. Create a new test class in `test_app.py`
2. Inherit from `unittest.TestCase`
3. Add test methods starting with `test_`
4. Use `setUp()` and `tearDown()` for test initialization/cleanup
5. Add the test class to the `test_classes` list in `run_tests()`

Example:

```python
class TestNewService(unittest.TestCase):
    def setUp(self):
        # Initialize test environment
        pass
    
    def tearDown(self):
        # Clean up test environment
        pass
    
    def test_new_functionality(self):
        # Test implementation
        self.assertTrue(True)
```

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: python run_tests.py
```

The test runner returns appropriate exit codes (0 for success, 1 for failure) for CI integration. 
