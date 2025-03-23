from pages.base_page import BasePage
import re

class ManagerPage(BasePage):
    """Page object for the bank manager page."""
    
    # Selectors
    ADD_CUSTOMER_TAB = "button[ng-click='addCust()']"
    OPEN_ACCOUNT_TAB = "button[ng-click='openAccount()']"
    CUSTOMERS_TAB = "button[ng-click='showCust()']"
    FIRST_NAME_INPUT = "input[placeholder='First Name']"
    LAST_NAME_INPUT = "input[placeholder='Last Name']"
    POST_CODE_INPUT = "input[placeholder='Post Code']"
    ADD_CUSTOMER_BTN = "button[type='submit']"
    CUSTOMER_SELECT = "#userSelect"
    CURRENCY_SELECT = "#currency"
    PROCESS_BTN = "button:text('Process')"
    CUSTOMERS_TABLE = "table.table.table-bordered.table-striped"
    CUSTOMER_ROWS = "table.table tbody tr"
    DELETE_BUTTON = "button:text('Delete')"
    SEARCH_CUSTOMER = "input[placeholder='Search Customer']"
    
    def go_to_add_customer(self):
        """Navigate to the Add Customer tab."""
        self.click(self.ADD_CUSTOMER_TAB)
    
    def go_to_open_account(self):
        """Navigate to the Open Account tab."""
        self.click(self.OPEN_ACCOUNT_TAB)
    
    def go_to_customers_list(self):
        """Navigate to the Customers tab."""
        self.click(self.CUSTOMERS_TAB)
    
    def add_customer(self, first_name: str, last_name: str, post_code: str):
        """Add a new customer."""
        self.go_to_add_customer()
        self.fill(self.FIRST_NAME_INPUT, first_name)
        self.fill(self.LAST_NAME_INPUT, last_name)
        self.fill(self.POST_CODE_INPUT, post_code)
        
        # Set up dialog handler before clicking
        self.page.once("dialog", lambda dialog: dialog.accept())
        
        # Submit the form
        self.click(self.ADD_CUSTOMER_BTN)
    
    def open_account(self, customer_name: str, currency: str):
        """Open a new account for a customer with specified currency."""
        self.go_to_open_account()
        
        # Select customer and currency
        self.select_option(self.CUSTOMER_SELECT, customer_name)
        self.select_option(self.CURRENCY_SELECT, currency)
        
        # Initialize account number
        self.account_number = None
        
        # Set up dialog handler before clicking
        def handle_dialog(dialog):
            # Log the actual dialog message for debugging
            print(f"Dialog message: {dialog.message}")
            
            # Set a default account number in case we can't extract it
            self.account_number = "unknown"
                
            # The dialog shows: "Account created successfully with account Number :XXXX"
            pattern = r"Account created successfully with account Number :(\d+)"
            
            # Extract the account number using the pattern
            match = re.search(pattern, dialog.message)
            if match:
                self.account_number = match.group(1)
                
            dialog.accept()
            
        self.page.once("dialog", handle_dialog)
        
        # Process the account creation
        self.click(self.PROCESS_BTN)
        self.page.wait_for_timeout(500)  # Increased wait time for dialog processing
        
        # Return the account number captured from the dialog
        return getattr(self, 'account_number', None)
    
    def delete_customer(self, customer_name: str):
        """Delete a customer by name."""
        self.go_to_customers_list()
        
        # Wait for the table to be fully loaded
        self.page.wait_for_selector(self.CUSTOMERS_TABLE, state="visible", timeout=500)
        
        # Search for the customer to ensure we get the right one
        self.fill(self.SEARCH_CUSTOMER, customer_name)
        self.page.wait_for_timeout(500)  # Wait for search results
        
        # Find the row containing the customer name
        rows = self.page.locator(self.CUSTOMER_ROWS)
        count = rows.count()
        delete_button = None
        
        for i in range(count):
            row = rows.nth(i)
            row_text = row.text_content()
            if customer_name in row_text:
                # Find delete button within this row
                delete_button = row.locator("button:text('Delete')")
                break
        
        if delete_button and delete_button.count() > 0:
            delete_button.click()
            self.page.wait_for_timeout(500)  # Wait for deletion to complete
            return True
        
        return False
    
    def is_customer_listed(self, customer_name: str):
        """Check if a customer is listed in the customers table."""
        self.go_to_customers_list()
        
        # Wait for the table to be fully loaded
        self.page.wait_for_selector(self.CUSTOMERS_TABLE, state="visible", timeout=500)
        
        # Get table content before searching to check if customer exists
        table_content = self.page.locator(self.CUSTOMERS_TABLE).text_content()
        if customer_name in table_content:
            return True
            
        # Try searching for the customer as backup
        self.fill(self.SEARCH_CUSTOMER, customer_name)
        self.page.wait_for_timeout(500)  # Increased wait time for search results
        

        table_content = self.page.locator(self.CUSTOMERS_TABLE).text_content()
        return customer_name in table_content