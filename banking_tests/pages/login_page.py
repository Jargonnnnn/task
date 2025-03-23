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
        # Wait for the button to be visible with increased timeout
        self.page.wait_for_selector(self.MANAGER_LOGIN_BTN, state="visible", timeout=5000)
        self.page.locator(self.MANAGER_LOGIN_BTN).click()
        # Wait for navigation to complete
        self.page.wait_for_timeout(1000)
        
    def is_at_customer_selection(self) -> bool:
        """Check if at customer selection screen."""
        # Wait a short time to make sure page has loaded properly
        self.page.wait_for_timeout(500)
        
        # Check for customer dropdown visibility
        dropdown_visible = self.is_visible(self.USER_SELECT)
        
        # Also check for "Your Name :" label as additional verification
        name_label = self.page.locator("text='Your Name :'")
        label_visible = name_label.is_visible() if name_label.count() > 0 else False
        
        return dropdown_visible and label_visible 