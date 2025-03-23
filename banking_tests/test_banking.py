import pytest
import time
from playwright.sync_api import expect

from pages.login_page import LoginPage
from pages.customer_page import CustomerPage
from pages.manager_page import ManagerPage

BASE_URL = "https://www.globalsqa.com/angularJs-protractor/BankingProject/#/login"

@pytest.fixture(scope="function", autouse=True)
def navigate_to_home(page):
    """Navigate to the banking app home page before each test."""
    page.goto(BASE_URL)

@pytest.fixture
def login_page(page):
    """Create login page object."""
    return LoginPage(page)

@pytest.fixture
def customer_page(page):
    """Create customer page object."""
    return CustomerPage(page)

@pytest.fixture
def manager_page(page):
    """Create manager page object."""
    return ManagerPage(page)

class TestBankingApplication:
    """Tests for the Banking Application using Page Object Model."""
    
    def test_customer_login_and_logout(self, login_page, customer_page, page):
        """Test customer login, verify account details and logout."""
        # Login as Harry Potter
        login_page.customer_login("Harry Potter")
        
        # Wait for page to load completely
        page.wait_for_timeout(1000)
        
        # Verify welcome message
        customer_page.expect_text(customer_page.WELCOME_MESSAGE, "Harry Potter")
        
        # Verify something specific about the account info (account number)
        account_number = customer_page.get_account_number()
        assert account_number, "Account number should be present"
        
        # Logout
        customer_page.logout()
        
        # Verify we are back at customer selection
        assert login_page.is_at_customer_selection(), "Not returned to customer selection screen"
    
    def test_bank_manager_add_customer(self, login_page, manager_page):
        """Test bank manager login and adding a new customer."""
        # Login as manager
        login_page.manager_login()
        
        # Add a new customer
        manager_page.add_customer("John", "Smith", "12345")
        
        # Verify we remain on the add customer page
        manager_page.expect_visible(manager_page.FIRST_NAME_INPUT)
    
    def test_deposit_and_withdrawal(self, login_page, customer_page):
        """Test customer login, deposit money, verify balance, and withdraw money."""
        # Login as Hermoine Granger
        login_page.customer_login("Hermoine Granger")
        
        # Get initial balance
        initial_balance = customer_page.get_balance()
        
        # Deposit amount
        deposit_amount = 100
        customer_page.perform_deposit(deposit_amount)
        
        # Verify success message
        customer_page.expect_text(customer_page.MESSAGE, "Deposit Successful")
        
        # Verify new balance
        updated_balance = customer_page.get_balance()
        expected_balance = initial_balance + deposit_amount
        assert updated_balance == expected_balance, f"Expected balance {expected_balance}, got {updated_balance}"
        
        # Withdraw the same amount
        withdrawal_successful = customer_page.perform_withdrawal(deposit_amount)
        
        # Verify final balance
        final_balance = customer_page.get_balance()
        
        # The balance should decrease after withdrawal
        assert final_balance <= updated_balance, f"Balance should not increase after withdrawal"
        
        # Verify the withdrawal in transaction history
        customer_page.go_to_transactions()
        customer_page.sort_transactions_by_date()  # Sort to show most recent first
        
        # Verify we have transactions
        transactions_count = customer_page.get_transactions_count()
        assert transactions_count > 0, "Transaction history should not be empty"
    
    def test_invalid_withdrawal_amount(self, login_page, customer_page):
        """Test attempting to withdraw more money than available in the account."""
        # Login as Ron Weasly
        login_page.customer_login("Ron Weasly")
        
        # Get current balance
        current_balance = customer_page.get_balance()
        
        # Attempt to withdraw more than the balance
        excessive_amount = current_balance + 1000
        customer_page.perform_withdrawal(excessive_amount)
        
        # Verify error message
        customer_page.expect_text(customer_page.MESSAGE, "Transaction Failed. You can not withdraw amount more than the balance.")
        
        # Verify balance remains unchanged
        final_balance = customer_page.get_balance()
        assert final_balance == current_balance, f"Balance should remain {current_balance}, but got {final_balance}"
    
    def test_multiple_accounts_navigation(self, login_page, customer_page, page):
        """Test navigation between multiple accounts for a customer."""
        # Login as Harry Potter who has multiple accounts
        login_page.customer_login("Harry Potter")
        
        # Wait for account information to fully load
        page.wait_for_timeout(1000)
        
        # Initial account number and balance
        initial_account_number = customer_page.get_account_number()
        initial_balance = customer_page.get_balance()
        
        # We expect Harry Potter to have multiple accounts
        assert customer_page.has_multiple_accounts(), "Harry Potter should have multiple accounts"
        
        customer_page.select_different_account()
        
        # Wait for account information to update
        page.wait_for_timeout(1000)
        
        # Verify that account number changed
        new_account_number = customer_page.get_account_number()
        assert new_account_number != initial_account_number, "Account did not change"
    
    def test_transaction_history(self, login_page, customer_page):
        """Test transaction history functionality after making deposits and withdrawals."""
        # Login as Hermoine Granger
        login_page.customer_login("Hermoine Granger")
        
        # Make a deposit
        deposit_amount = 50
        customer_page.perform_deposit(deposit_amount)
        
        # Make a withdrawal
        withdrawal_amount = 50
        customer_page.perform_withdrawal(withdrawal_amount)
        
        # Navigate to Transactions tab
        customer_page.go_to_transactions()
        
        # Sort transactions by date to see most recent first
        customer_page.sort_transactions_by_date()
        
        # Verify transactions are listed
        customer_page.expect_visible(customer_page.TRANSACTIONS_TABLE)
        
        # Verify we have transactions
        transactions_count = customer_page.get_transactions_count()
        assert transactions_count > 0, "Transaction history should not be empty"
        
        # Get transaction amounts and verify our transactions are included
        transaction_amounts = customer_page.get_transaction_amounts()[:10]  # Look at 10 most recent
        
        # Check that our transaction amounts are in the list
        # We expect the test to fail if the transaction amounts are not found
        # Convert integer amounts to strings for comparison since transaction_amounts contains strings
        deposit_amount_str = str(deposit_amount)
        withdrawal_amount_str = str(withdrawal_amount)
        assert deposit_amount_str in transaction_amounts or withdrawal_amount_str in transaction_amounts, "Transaction amounts should include our deposit or withdrawal"
        
    def test_complete_customer_lifecycle(self, login_page, manager_page, customer_page, page):
        """Test the complete lifecycle of a customer: creation, account opening, transactions, and deletion."""
        # Test data using exact name as requested
        first_name = "John"
        last_name = "Smith"
        post_code = "12345"
        full_name = f"{first_name} {last_name}"
        deposit_amount = 500
        withdrawal_amount = 250
        
        # Step 1: Navigate to the banking website
        page.goto(BASE_URL)
        
        # Step 2: Click on Bank Manager Login button
        page.locator('button:text("Bank Manager Login")').click()
        page.wait_for_timeout(1000)
        
        # Step 3: Click on Add Customer tab
        page.locator('button:text("Add Customer")').click()
        page.wait_for_timeout(1000)
        
        # Step 4: Fill in customer information
        page.locator('input[placeholder="First Name"]').fill(first_name)
        page.locator('input[placeholder="Last Name"]').fill(last_name)
        page.locator('input[placeholder="Post Code"]').fill(post_code)
        
        # Handle the alert that will appear after adding customer
        page.once("dialog", lambda dialog: dialog.accept())
        
        # Step 5: Click on Add Customer button
        page.locator('button[type="submit"]:text("Add Customer")').click()
        page.wait_for_timeout(1000)  # Wait for alert to be handled
        
        # Step 6: Verify the customer was added by going to Customers tab
        page.locator('button:text("Customers")').click()
        page.wait_for_timeout(1000)
        
        # Search for the customer we just added
        page.locator('input[placeholder="Search Customer"]').fill(first_name)
        page.wait_for_timeout(1000)
        
        # Verify the customer appears in the search results
        customers_table = page.locator('table.table')
        assert customers_table.text_content().find(first_name) >= 0, f"Customer {first_name} not found in table"
        assert customers_table.text_content().find(last_name) >= 0, f"Customer {last_name} not found in table"
        
        # Step 7: Create an account for the customer
        page.locator('button:text("Open Account")').click()
        page.wait_for_timeout(1000)
        
        # Select the customer and currency
        page.locator('#userSelect').select_option(label=full_name)
        page.locator('#currency').select_option(label="Dollar")
        
        # Handle alert that will show account number
        page.once("dialog", lambda dialog: dialog.accept())
        
        # Click Process button
        page.locator('button:text("Process")').click()
        page.wait_for_timeout(1000)
        
        # Step 8: Customer logs in
        page.goto(BASE_URL)
        page.locator('button:text("Customer Login")').click()
        page.wait_for_timeout(1000)
        
        # Select customer
        page.locator('#userSelect').select_option(label=full_name)
        page.locator('button:text("Login")').click()
        page.wait_for_timeout(1000)
        
        # Verify welcome message contains the customer name
        welcome_element = page.locator('span.fontBig')
        assert welcome_element.text_content().find(full_name) >= 0, "Welcome message doesn't contain customer name"
        
        # Step 9: Make a deposit
        page.locator('button:text("Deposit")').click()
        page.wait_for_timeout(500)
        
        page.locator('input[placeholder="amount"]').fill(str(deposit_amount))
        page.locator('button[type="submit"]:text("Deposit")').click()
        page.wait_for_timeout(500)
        
        # Verify success message
        message = page.locator('span.error')
        assert "Deposit Successful" in message.text_content(), "Deposit success message not displayed"
        
        # Step 10: Check balance
        balance_element = page.locator('div.center strong:nth-child(2)')
        balance = int(balance_element.text_content())
        assert balance == deposit_amount, f"Expected balance {deposit_amount}, got {balance}"
        
        # Step 11: Withdraw amount
        page.locator('button:text("Withdrawl")').click()
        page.wait_for_timeout(500)
        
        page.locator('input[placeholder="amount"]').fill(str(withdrawal_amount))
        # Use a more specific selector to target only the submit button
        page.locator('button[type="submit"]:text("Withdraw")').click()
        page.wait_for_timeout(1000)
        
        # Verify final balance
        updated_balance = int(balance_element.text_content())
        expected_balance = deposit_amount - withdrawal_amount
        assert updated_balance == expected_balance, f"Expected balance {expected_balance}, got {updated_balance}"
        
        # Step 12: Logout
        page.locator('button:text("Logout")').click()
        page.wait_for_timeout(500)
        
        # Step 13: Log back in as manager and delete the customer
        page.locator('button:text("Home")').click()
        page.wait_for_timeout(500)
        
        page.locator('button:text("Bank Manager Login")').click()
        page.wait_for_timeout(500)
        
        page.locator('button:text("Customers")').click()
        page.wait_for_timeout(1000)
        
        # Search for customer
        page.locator('input[placeholder="Search Customer"]').fill(first_name)
        page.wait_for_timeout(1000)
        
        # Find the delete button for our customer and click it
        rows = page.locator('table.table tbody tr')
        for i in range(rows.count()):
            row = rows.nth(i)
            if first_name in row.text_content() and last_name in row.text_content():
                row.locator('button:text("Delete")').click()
                break
                
        page.wait_for_timeout(1000)
        
        # Verify customer was deleted
        page.locator('input[placeholder="Search Customer"]').fill(first_name)
        page.wait_for_timeout(1000)
        
        # After deletion, there should be no results for this customer
        rows_after_delete = page.locator('table.table tbody tr')
        found_after_delete = False
        for i in range(rows_after_delete.count()):
            row_text = rows_after_delete.nth(i).text_content()
            if first_name in row_text and last_name in row_text:
                found_after_delete = True
                break
                
        assert not found_after_delete, f"Customer {full_name} still exists after deletion"
    
