import pytest
import logging
import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """Called before each test is run."""
    logging.info(f"▶️ STARTING TEST: {item.name}")
    
@pytest.hookimpl(trylast=True)
def pytest_runtest_teardown(item):
    """Called after each test is completed."""
    logging.info(f"⏹️ FINISHED TEST: {item.name}\n" + "-"*80)

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Generate a report for each test phase (setup, call, teardown)."""
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call":
        # Only log the outcome after the test execution (call phase)
        if report.passed:
            logging.info(f"TEST PASSED: {item.name}")
        elif report.failed:
            logging.error(f"TEST FAILED: {item.name}")
            if hasattr(report, "longrepr"):
                logging.error(f"ERROR DETAILS: {report.longreprtext}")
        elif report.skipped:
            logging.info(f"TEST SKIPPED: {item.name}")

@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """Called after the test session is completed."""
    outcome = "PASSED" if exitstatus == 0 else "FAILED"
    logging.info(f"TEST SESSION COMPLETE - Status: {outcome}")
    logging.info(f"Total test count: {session.testscollected}")
    logging.info(f"Passed test count: {session.testscollected - session.testsfailed}")
    logging.info(f"Failed test count: {session.testsfailed}")

@pytest.fixture(scope="session")
def browser_type():
    """Launch the browser only once per session."""
    with sync_playwright() as playwright:
        # Using Chromium by default but could be configured to use other browsers
        browser_type = playwright.chromium
        yield browser_type

@pytest.fixture(scope="session")
def browser(browser_type):
    """Create a shared browser instance for all tests."""
    browser = browser_type.launch(headless=True)
    yield browser
    browser.close()

@pytest.fixture(scope="function")
def context(browser):
    """Create a new browser context for each test function."""
    context = browser.new_context()
    yield context
    context.close()

@pytest.fixture(scope="function")
def page(context):
    """Create a new page for each test."""
    page = context.new_page()
    yield page
    page.close() 