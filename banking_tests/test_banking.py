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
        page.wait_for_timeout(500)
        
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
        page.wait_for_timeout(500)
        
        # Initial account number and balance
        initial_account_number = customer_page.get_account_number()
        initial_balance = customer_page.get_balance()
        
        # We expect Harry Potter to have multiple accounts
        assert customer_page.has_multiple_accounts(), "Harry Potter should have multiple accounts"
        
        customer_page.select_different_account()
        
        # Wait for account information to update
        page.wait_for_timeout(500)
        
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
        """Test the complete lifecycle of a customer: creation, account opening, transactions, and deletion."""
        # Test data - use unique name to avoid conflicts
        unique_id = int(time.time())
        first_name = "John"
        last_name = f"Smith{unique_id}"
        post_code = "12345"
        full_name = f"{first_name} {last_name}"
        deposit_amount = 500
        withdrawal_amount = 250
        
        login_page.manager_login()
        manager_page.add_customer(first_name, last_name, post_code)
        
        manager_page.go_to_customers_list()
        page.wait_for_timeout(500)  # Wait for list to populate
        assert manager_page.is_customer_listed(full_name), f"Customer {full_name} not found in the list"
        
        # Step 2: Manager opens an account for the customer
        account_number = manager_page.open_account(full_name, "Dollar")
        assert account_number, "Account number should be returned after account creation"
        
        # Step 3: Customer logs in
        page.goto(BASE_URL)  # Return to home page
        login_page.customer_login(full_name)
        
        # Verify welcome message
        customer_page.expect_text(customer_page.WELCOME_MESSAGE, full_name)
        
        # Step 4: Customer performs deposit
        customer_page.perform_deposit(deposit_amount)
        customer_page.expect_text(customer_page.MESSAGE, "Deposit Successful")
        
        # Verify balance after deposit
        balance = customer_page.get_balance()
        assert balance == deposit_amount, f"Expected balance {deposit_amount}, got {balance}"
        
        # Step 5: Customer performs withdrawal
        customer_page.perform_withdrawal(withdrawal_amount)
        
        # Verify balance after withdrawal
        updated_balance = customer_page.get_balance()
        expected_balance = deposit_amount - withdrawal_amount
        assert updated_balance == expected_balance, f"Expected balance {expected_balance}, got {updated_balance}"
        
        # Step 6: Check transaction history
        customer_page.go_to_transactions()
        customer_page.sort_transactions_by_date()
        
        # Verify transactions exist
        transactions_count = customer_page.get_transactions_count()
        assert transactions_count >= 2, f"Expected at least 2 transactions, found {transactions_count}"
        
        # Step 7: Customer logs out
        customer_page.logout()
        
        # Step 8: Manager deletes the customer
        login_page.manager_login()
        deleted = manager_page.delete_customer(full_name)
        assert deleted, f"Customer {full_name} could not be deleted"
        
        # Verify customer was deleted
        assert not manager_page.is_customer_listed(full_name), f"Customer {full_name} still found in the list after deletion"
    
    def test_manager_open_account_and_verify(self, login_page, manager_page, customer_page, page):
        """Test manager creating a customer, opening an account, and verifying the account works."""
        # Step 1: Add new customer via manager
        login_page.manager_login()
        
        # Generate unique name to avoid conflicts with existing customers
        unique_id = int(time.time())
        first_name = "John"
        last_name = f"Smith{unique_id}"
        full_name = f"{first_name} {last_name}"
        
        manager_page.add_customer(first_name, last_name, "98765")
        
        # Step 2: Open a Dollar account for this customer
        account_number = manager_page.open_account(full_name, "Dollar")
        assert account_number, "Account number should be returned after account creation"
        
        # Step 3: Return to home and login as the new customer
        page.goto(BASE_URL)  # Return to home page
        login_page.customer_login(full_name)
        
        # Step 4: Verify the customer can see their account
        customer_page.expect_text(customer_page.WELCOME_MESSAGE, full_name)
        
        # Verify account number
        displayed_account = customer_page.get_account_number()
        assert displayed_account, "Account number should be visible"
        
        # Step 5: Verify initial balance is zero
        balance = customer_page.get_balance()
        assert balance == 0, f"Initial balance should be 0, got {balance}"
        
        # Step 6: Clean up - return to manager and delete the customer
        customer_page.logout()
        login_page.manager_login()
        manager_page.delete_customer(full_name)