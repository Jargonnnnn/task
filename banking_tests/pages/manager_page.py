from pages.base_page import BasePage

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