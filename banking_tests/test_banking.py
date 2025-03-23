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
        
        # Verify welcome message
        customer_page.expect_text(customer_page.WELCOME_MESSAGE, "Harry Potter")
        
        # Verify something specific about the account info (account number)
        account_number = customer_page.get_account_number()
        assert account_number, "Account number should be present"
        
        # Logout - explicitly stay on customer selection screen (don't go to home)
        customer_page.logout(return_to_home=False)
        
        # Wait a moment for the page transition to complete
        page.wait_for_timeout(1000)
        
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
        
        # Initial account number and balance
        initial_account_number = customer_page.get_account_number()
        initial_balance = customer_page.get_balance()
        
        # We expect Harry Potter to have multiple accounts
        assert customer_page.has_multiple_accounts(), "Harry Potter should have multiple accounts"
        
        customer_page.select_different_account()

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
        deposit_amount_str = str(deposit_amount)
        withdrawal_amount_str = str(withdrawal_amount)
        assert deposit_amount_str in transaction_amounts or withdrawal_amount_str in transaction_amounts, "Transaction amounts should include our deposit or withdrawal"
        
    def test_complete_customer_lifecycle(self, login_page, manager_page, customer_page, page):
        """Test the complete lifecycle of a customer: creation, account opening, transactions, and deletion
        using Page Object Models for better test organization and maintenance.
        """
        # Test data - use unique name to avoid conflicts
        unique_id = int(time.time())
        first_name = "John"
        last_name = f"Smith{unique_id}"
        post_code = "12345"
        full_name = f"{first_name} {last_name}"
        deposit_amount = 500
        withdrawal_amount = 250
        currency = "Dollar"
        
        # Step 1: Login as bank manager
        login_page.manager_login()
        
        # Step 2: Create a new customer
        manager_page.go_to_add_customer()
        manager_page.add_customer(first_name, last_name, post_code)
        
        # Step 3: Verify the customer was added with increased wait time
        manager_page.go_to_customers_list()
        page.wait_for_timeout(1000)  # Wait for the table to fully update
        customer_found = manager_page.is_customer_listed(full_name)
        assert customer_found, f"Customer {full_name} not found in table"
        
        # Step 4: Create an account for the customer
        manager_page.go_to_open_account()
        account_number = manager_page.open_account(full_name, currency)
        
        # Step 5: Customer logs in
        page.goto(BASE_URL)  # Navigate back to home
        login_page.customer_login(full_name)
        
        # Step 6: Verify welcome message
        customer_page.expect_text(customer_page.WELCOME_MESSAGE, full_name)
        
        # Step 7: Make a deposit
        customer_page.perform_deposit(deposit_amount)
        
        # Step 8: Verify success message and balance
        customer_page.expect_text(customer_page.MESSAGE, "Deposit Successful")
        balance = customer_page.get_balance()
        assert balance == deposit_amount, f"Expected balance {deposit_amount}, got {balance}"
        
        # Step 9: Withdraw amount
        customer_page.perform_withdrawal(withdrawal_amount)
        
        # Step 10: Verify final balance
        updated_balance = customer_page.get_balance()
        expected_balance = deposit_amount - withdrawal_amount
        assert updated_balance == expected_balance, f"Expected balance {expected_balance}, got {updated_balance}"
        
        # Step 11: Check transaction history
        customer_page.go_to_transactions()
        customer_page.sort_transactions_by_date()
        
        # Step 12: Verify transactions are listed
        customer_page.expect_visible(customer_page.TRANSACTIONS_TABLE)
        
        # Step 13: Verify we have at least two transactions
        transactions_count = customer_page.get_transactions_count()
        assert transactions_count >= 2, f"Expected at least 2 transactions, found {transactions_count}"
        
        # Step 14: Customer logs out and returns to home page
        customer_page.logout(return_to_home=True)
        
        # Step 15: Log back in as manager and delete the customer
        login_page.manager_login()
        manager_page.go_to_customers_list()
        
        # Step 16: Delete customer and verify
        manager_page.delete_customer(full_name)
        page.wait_for_timeout(1000)  # Wait for the table to fully update
        customer_still_exists = manager_page.is_customer_listed(full_name)
        assert not customer_still_exists, f"Customer {full_name} still found after deletion"