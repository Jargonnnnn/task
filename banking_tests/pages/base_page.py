from playwright.sync_api import Page, expect

class BasePage:
    """Base page object containing common methods and utilities."""
    
    def __init__(self, page: Page):
        self.page = page
        
    def navigate_to(self, url: str):
        """Navigate to a specific URL."""
        self.page.goto(url)
        
    def get_text(self, selector: str) -> str:
        """Get text content of an element."""
        return self.page.locator(selector).text_content()
        
    def click(self, selector: str):
        """Click on an element."""
        self.page.locator(selector).click()
        
    def fill(self, selector: str, value: str):
        """Fill a form field."""
        self.page.locator(selector).fill(value)
        
    def select_option(self, selector: str, option: str):
        """Select an option from a dropdown."""
        self.page.locator(selector).select_option(label=option)
        
    def is_visible(self, selector: str) -> bool:
        """Check if an element is visible."""
        return self.page.locator(selector).is_visible()
        
    def expect_text(self, selector: str, text: str, timeout=5000):
        """Expect an element to contain specific text with custom timeout."""
        expect(self.page.locator(selector)).to_contain_text(text, timeout=timeout)
        
    def expect_visible(self, selector: str):
        """Expect an element to be visible."""
        expect(self.page.locator(selector)).to_be_visible() 