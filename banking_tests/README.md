# Banking Website Automated Tests

This project contains automated tests for the banking demo website at [GlobalSQA Banking Project](https://www.globalsqa.com/angularJs-protractor/BankingProject/#/login).

## Test Scenarios

Six comprehensive test scenarios are implemented:

### Core Functionality Tests
1. **Customer Login and Logout**: Validates a customer can log in, view account details, and log out.
2. **Add Customer**: Tests bank manager functionality to add a new customer.
3. **Deposit and Withdrawal**: Verifies deposit and withdrawal operations, including balance verification.

### Enhanced Test Coverage
4. **Invalid Withdrawal Amount**: Tests system validation when attempting to withdraw more money than available in the account.
5. **Multiple Accounts Navigation**: Tests switching between multiple accounts for a customer and verifies that account-specific data is correctly displayed.
6. **Transaction History**: Verifies the transaction history functionality after making deposits and withdrawals.

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation and Setup

Follow these steps to set up the test environment:

1. Clone the repository (or download the project files)

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
   
   Alternatively, you can install dependencies directly:
   ```
   pip install pytest==8.3.5 playwright==1.47.0 pytest-playwright==0.7.0 pytest-json-report==1.5.0
   ```

3. Install Playwright browsers:
   ```
   python -m playwright install chromium
   ```
   
   For headful browser testing (with visible browser):
   ```
   python -m playwright install chromium --with-deps
   ```

## Running the Tests

After completing the setup, run the tests using:

```
python run_tests.py
```

This will:
- Run all tests
- Generate JSON test reports
- Display test results
- Report proper exit codes

## JSON Reporting

The test suite uses JSON reporting to provide detailed information about test execution:

1. **Test Results**: Test results are saved in JSON format at `test_results.json`
2. **Playwright Results**: Detailed Playwright results are saved at `results/playwright_report.json`
3. **Results Structure**: The JSON report includes:
   - Test summary statistics
   - Detailed information about test execution
   - Pass/fail status of each test
   - Test durations
   - Error messages for failing tests

## Potential Improvements

With more time used, the following improvements could be made:

1. Add data-driven tests for different customers and amounts
2. Implement configuration management for environment variables
3. Add visual verification for UI components
4. Add parallel test execution capabilities
5. Integrate with CI/CD pipelines