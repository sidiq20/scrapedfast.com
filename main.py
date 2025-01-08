import logging
import threading
import tkinter as tk
from tkinter import ttk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class InternetSpeedScraper:
    def __init__(self, url='https://fast.com', wait_time=60, element_id='speed-value'):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Headless mode
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.url = url
        self.wait_time = wait_time
        self.element_id = element_id

    def load_page(self):
        """Load the specified URL."""
        logging.info(f"Loading the page: {self.url}")
        self.driver.get(self.url)

    def wait_for_speed_result(self):
        """Wait for the speed value to update from the initial placeholder."""
        logging.info("Waiting for the speed result to update.")
        try:
            WebDriverWait(self.driver, self.wait_time).until(
                lambda driver: driver.find_element(By.ID, self.element_id).text != "0"
            )
        except TimeoutException:
            logging.error("Timed out waiting for the speed value to update.")
            raise

    def extract_speed(self):
        """Extract the internet speed from the loaded page."""
        logging.info("Extracting the speed value from the page.")
        try:
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            speed_element = soup.find('div', {'id': self.element_id})
            if speed_element:
                speed = speed_element.text.strip()
                logging.info(f"Extracted speed: {speed} Mbps")
                return speed
            else:
                logging.error("Speed value element not found.")
                return None
        except NoSuchElementException:
            logging.error("Speed value element not found.")
            return None

    def cleanup(self):
        """Close the Selenium WebDriver."""
        logging.info("Cleaning up and closing the WebDriver.")
        self.driver.quit()

    def get_internet_speed(self):
        """Main method to get the internet speed."""
        try:
            self.load_page()
            self.wait_for_speed_result()
            speed = self.extract_speed()
            return speed
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return None
        finally:
            self.cleanup()

class SpeedTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Internet Speed Test")

        # Styling with custom fonts and colors
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Helvetica", 12), padding=10)
        self.style.configure("TLabel", font=("Helvetica", 12), padding=10)

        # Frame for the content
        self.frame = ttk.Frame(root, padding=20)
        self.frame.pack(expand=True, fill='both')

        # Title Label
        self.title_label = ttk.Label(self.frame, text="Internet Speed Test", font=("Helvetica", 18, "bold"), foreground="blue")
        self.title_label.pack(pady=(0, 20))

        # Button to start the test
        self.test_button = ttk.Button(self.frame, text="Start Test", command=self.start_test)
        self.test_button.pack(pady=(0, 10))

        # Progress bar
        self.progress = ttk.Progressbar(self.frame, mode='indeterminate')
        self.progress.pack(pady=(0, 10), fill='x')

        # Result Label
        self.result_label = ttk.Label(self.frame, text="Click 'Start Test' to check your speed.", font=("Helvetica", 12))
        self.result_label.pack(pady=(0, 20))

    def start_test(self):
        """Start the internet speed test in a separate thread."""
        self.result_label.config(text="Testing, please wait...")
        self.progress.start()
        threading.Thread(target=self.run_speed_test).start()

    def run_speed_test(self):
        """Run the speed test and update the result in the GUI."""
        scraper = InternetSpeedScraper()
        speed = scraper.get_internet_speed()
        self.progress.stop()
        if speed:
            self.result_label.config(text=f"Your internet speed is {speed} Mbps")
        else:
            self.result_label.config(text="Failed to retrieve the internet speed.")

# Create the main window
if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedTestApp(root)
    root.mainloop()
