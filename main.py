from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class InternetSpeedScraper:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Headless mode
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def load_fast_com(self):
        """Load the fast.com website and wait for the speed to appear."""
        self.driver.get('https://fast.com')
        WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.ID, "speed-value"))
        )

    def extract_speed(self):
        """Extract the internet speed from the loaded page."""
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        speed_element = soup.find('div', {'id': 'speed-value'})
        speed = speed_element.text.strip()
        return speed

    def cleanup(self):
        """Close the Selenium WebDriver."""
        self.driver.quit()

    def get_internet_speed(self):
        """Main method to get the internet speed."""
        try:
            self.load_fast_com()
            speed = self.extract_speed()
            return speed
        finally:
            self.cleanup()

# Example usage
if __name__ == "__main__":
    scraper = InternetSpeedScraper()
    speed = scraper.get_internet_speed()
    print(f"Your internet speed is {speed} Mbps")
