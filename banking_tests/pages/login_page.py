from pages.base_page import BasePage

class LoginPage(BasePage):
    """Page object for the login page."""
    
    # Selectors
    CUSTOMER_LOGIN_BTN = "button[ng-click='customer()']"
    MANAGER_LOGIN_BTN = "button[ng-click='manager()']"
    USER_SELECT = "#userSelect"
    LOGIN_BTN = "button:text('Login')"
    
    def customer_login(self, customer_name: str):
        """Login as a customer."""
        self.page.locator(self.CUSTOMER_LOGIN_BTN).click()
        self.select_option(self.USER_SELECT, customer_name)
        self.page.locator(self.LOGIN_BTN).click()
        
    def manager_login(self):
        """Login as a bank manager."""
        self.page.locator(self.MANAGER_LOGIN_BTN).click()
        
    def is_at_customer_selection(self) -> bool:
        """Check if at customer selection screen."""
        return self.is_visible(self.USER_SELECT) 