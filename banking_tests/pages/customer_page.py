from pages.base_page import BasePage

class CustomerPage(BasePage):
    """Page object for the customer account page."""
    
    # Selectors
    WELCOME_MESSAGE = "span.fontBig"
    ACCOUNT_INFO = "div.center:first-child"
    BALANCE = "div.center strong:nth-child(2)"
    ACCOUNT_NUMBER = "div.center strong:nth-child(1)"
    LOGOUT_BTN = "button:text('Logout')"
    DEPOSIT_TAB = "button[ng-click='deposit()']"
    WITHDRAW_TAB = "button[ng-click='withdrawl()']"
    TRANSACTIONS_TAB = "button[ng-click='transactions()']"
    AMOUNT_INPUT = "input[placeholder='amount']"
    # More specific selectors to avoid ambiguity
    DEPOSIT_BTN = "form button[type='submit']:text('Deposit')"
    # The actual withdraw button doesn't have type='submit' in the HTML
    WITHDRAW_BTN = "form button.btn.btn-default:text('Withdraw')"
    MESSAGE = "span.error"
    ACCOUNTS_DROPDOWN = "#accountSelect"
    TRANSACTIONS_TABLE = "table.table"
    TRANSACTION_ROWS = "table.table tbody tr"
    TRANSACTION_AMOUNT_CELLS = "table.table tbody tr td:nth-child(2)"
    SORT_BY_DATE_BTN = "a[ng-click*='sortType = \\'date\\'']"
    
    def get_welcome_message(self) -> str:
        """Get the welcome message text."""
        return self.get_text(self.WELCOME_MESSAGE)
    
    def get_balance(self) -> int:
        """Get the current account balance."""
        balance_text = self.get_text(self.BALANCE)
        return int(balance_text)
    
    def get_account_number(self) -> str:
        """Get the current account number."""
        account_text = self.get_text(self.ACCOUNT_NUMBER)
        # Extract just the account number from text like "Account Number : 1004 ,"
        import re
        match = re.search(r'(\d+)', account_text)
        if match:
            return match.group(1)
        return account_text
    
    def logout(self):
        """Log out from customer account."""
        self.click(self.LOGOUT_BTN)
    
    def perform_deposit(self, amount: int):
        """Deposit funds into the account."""
        self.click(self.DEPOSIT_TAB)
        self.fill(self.AMOUNT_INPUT, str(amount))
        self.click(self.DEPOSIT_BTN)
    
    def perform_withdrawal(self, amount: int):
        """Withdraw funds from the account."""
        self.click(self.WITHDRAW_TAB)
        self.page.wait_for_timeout(500)  # Wait for the withdrawal form to be ready
        
        # Clear the input field first to ensure clean entry
        self.page.locator(self.AMOUNT_INPUT).clear()
        self.fill(self.AMOUNT_INPUT, str(amount))
        
        # Ensure we're clicking the visible button with correct text
        if self.page.locator(self.WITHDRAW_BTN).is_visible():
            self.page.locator(self.WITHDRAW_BTN).click()
        else:
            # Fallback to less specific selector if our specific one fails
            self.page.locator("button:text('Withdraw')").click()
            
        # Wait for any response after clicking withdraw
        self.page.wait_for_timeout(1000)
        
        # Return true if the message contains "successful"
        message_element = self.page.locator(self.MESSAGE)
        if message_element.is_visible():
            message_text = message_element.text_content()
            return "successful" in message_text.lower()
        return False
    
    def get_message(self) -> str:
        """Get the transaction message."""
        return self.get_text(self.MESSAGE)
    
    def has_multiple_accounts(self) -> bool:
        """Check if customer has multiple accounts."""
        dropdown = self.page.locator(self.ACCOUNTS_DROPDOWN)
        options = dropdown.evaluate("el => Array.from(el.options).map(o => o.value)")
        return len(options) > 1
    
    def select_different_account(self):
        """Select a different account from the dropdown."""
        dropdown = self.page.locator(self.ACCOUNTS_DROPDOWN)
        
        # Get all options with their index and text
        options = dropdown.evaluate("""el => {
            const selectedIndex = el.selectedIndex;
            return Array.from(el.options).map((opt, index) => { 
                return { 
                    text: opt.text, 
                    index: index,
                    selected: index === selectedIndex
                }; 
            });
        }""")
        
        # Filter out the currently selected option
        other_options = [opt for opt in options if not opt['selected']]
        
        if other_options:
            # Select the first different account by index
            dropdown.select_option(index=other_options[0]['index'])
            # Wait for the account data to load
            self.page.wait_for_timeout(1000)  # Increased timeout to ensure loading completes
    
    def select_account_by_number(self, account_number: str):
        """Select a specific account by account number."""
        dropdown = self.page.locator(self.ACCOUNTS_DROPDOWN)
        # Use index or label instead of value, as the account number might not be the value
        # Get all options and find the one with text containing the account number
        options = dropdown.evaluate("""el => {
            return Array.from(el.options).map((opt, index) => { 
                return { 
                    text: opt.text, 
                    index: index
                }; 
            });
        }""")
        
        # Find the option that contains the account number in its text
        for option in options:
            if account_number in option['text']:
                dropdown.select_option(index=option['index'])
                break
                
        # Wait for the account data to load
        self.page.wait_for_timeout(500)
    
    def go_to_transactions(self):
        """Navigate to the Transactions tab."""
        self.click(self.TRANSACTIONS_TAB)
        # Wait for transactions to load
        self.page.wait_for_timeout(1000)
        
    def sort_transactions_by_date(self):
        """Sort transactions by date (newest first)."""
        self.click(self.SORT_BY_DATE_BTN)
        # Wait for sorting to complete
        self.page.wait_for_timeout(500)
    
    def get_transactions_count(self) -> int:
        """Get the number of transaction rows in the table."""
        rows = self.page.locator(self.TRANSACTION_ROWS)
        return rows.count()
    
    def get_transaction_amounts(self) -> list:
        """Get all transaction amounts as a list of strings."""
        cells = self.page.locator(self.TRANSACTION_AMOUNT_CELLS)
        count = cells.count()
        amounts = []
        
        for i in range(count):
            amount_text = cells.nth(i).text_content().strip()
            amounts.append(amount_text)
        
        return amounts 