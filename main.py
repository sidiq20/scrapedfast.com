import logging
import threading
import tkinter as tk
from tkinter import ttk
from plyer import notification
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import subprocess
import re
import platform
import json
import csv  # Import the csv module
from datetime import datetime
import schedule
import time
import requests
import speedtest  # Correct import for speedtest


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class InternetSpeedScraper:
    def __init__(self, url='https://fast.com', wait_time=60, element_id='speed-value'):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Headless mode
        if platform.system().lower() == 'windows':
            options.add_argument('--disable-gpu')  # Windows-specific optimization
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

    def get_ping(self, host='google.com'):
        """Ping a host and return the average ping time."""
        logging.info(f"Pinging {host} to check the latency.")
        try:
            count_flag = '-n' if platform.system().lower() == 'windows' else '-c'
            result = subprocess.run(['ping', count_flag, '4', host], capture_output=True, text=True)
            if result.returncode == 0:
                match = re.search(r'Average = (\d+)ms' if platform.system().lower() == 'windows' else r'rtt.*=/ ([\d.]+)', result.stdout)
                if match:
                    ping_time = match.group(1)
                    logging.info(f"Average ping time: {ping_time} ms")
                    return ping_time
                else:
                    logging.error("Could not parse the ping output.")
            else:
                logging.error("Ping command failed.")
        except Exception as e:
            logging.error(f"An error occurred while checking the ping: {e}")
        return None

    def cleanup(self):
        """Close the Selenium WebDriver."""
        logging.info("Cleaning up and closing the WebDriver.")
        self.driver.quit()

    def get_internet_speed_and_ping(self):
        """Main method to get the internet speed and ping."""
        try:
            self.load_page()
            self.wait_for_speed_result()
            speed = self.extract_speed()
            ping = self.get_ping()
            return speed, ping
        except TimeoutException:
            logging.error("The speed test took too long to complete.")
            return None, None
        except WebDriverException as e:
            logging.error(f"WebDriver error: {e}")
            return None, None
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return None, None
        finally:
            self.cleanup()

    def save_result(self, speed, ping):
        """Save the result to a JSON file."""
        with open('results.json', 'a') as file:
            json.dump({'speed': speed, 'ping': ping, 'timestamp': str(datetime.now())}, file)
            file.write('\n')
        logging.info("Result saved successfully.")

    def run_speedtest(self):
        """Run a speed test using Speedtest.net."""
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download() / 1e6  # Convert to Mbps
        upload_speed = st.upload() / 1e6  # Convert to Mbps
        return download_speed, upload_speed

    def get_ping_with_jitter_and_loss(self, host='google.com'):
        """Ping a host and calculate jitter and packet loss."""
        count_flag = '-n' if platform.system().lower() == 'windows' else '-c'
        result = subprocess.run(['ping', count_flag, '10', host], capture_output=True, text=True)
        if result.returncode == 0:
            ping_times = re.findall(r'time=(\d+)', result.stdout)
            if ping_times:
                ping_times = list(map(int, ping_times))
                jitter = max(ping_times) - min(ping_times)
                packet_loss = 100 - (len(ping_times) / 10 * 100)
                return jitter, packet_loss
            else:
                logging.error("Could not parse the ping output.")
        else:
            logging.error("Ping command failed.")
        return None, None

def auto_detect_location():
    """Auto-detect the user's location using IP-based geolocation."""
    try:
        response = requests.get('https://ipinfo.io/json')
        data = response.json()
        city = data.get('city', 'London')  # Default to London if city is not found
        return city
    except Exception as e:
        logging.error(f"Error detecting location: {e}")
        return 'London'  # Fallback to a default city

def notify_user(title, message):
    """Send a desktop notification."""
    notification.notify(
        title=title,
        message=message,
        timeout=10
    )

class SpeedTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Internet Speed Test")

        self.style = ttk.Style()
        self.style.configure("TButton", font=("Helvetica", 12), padding=10)
        self.style.configure("TLabel", font=("Helvetica", 12), padding=10)

        self.frame = ttk.Frame(root, padding=20)
        self.frame.pack(expand=True, fill='both')

        self.title_label = ttk.Label(self.frame, text="Internet Speed Test", font=("Helvetica", 18, "bold"), foreground="blue")
        self.title_label.pack(pady=(0, 20))

        self.test_button = ttk.Button(self.frame, text="Start Test", command=self.start_test)
        self.test_button.pack(pady=(0, 10))

        self.progress = ttk.Progressbar(self.frame, mode='indeterminate')
        self.progress.pack(pady=(0, 10), fill='x')

        self.result_label = ttk.Label(self.frame, text="Click 'Start Test' to check your speed.", font=("Helvetica", 12))
        self.result_label.pack(pady=(0, 20))

        self.weather_label = ttk.Label(self.frame, font=("Helvetica", 12))
        self.weather_label.pack(pady=(0, 10))

        dark_mode_button = ttk.Button(self.frame, text="Dark Mode", command=self.toggle_dark_mode)
        dark_mode_button.pack(pady=(0, 10))

        export_button = ttk.Button(self.frame, text="Export Results", command=self.export_results_to_csv)
        export_button.pack(pady=(0, 10))

        self.schedule_test()

    def start_test(self):
        """Start the internet speed and ping test in a separate thread."""
        self.result_label.config(text="Testing, please wait...")
        self.progress.start()
        threading.Thread(target=self.run_speed_test).start()

    def run_speed_test(self):
        """Run the speed and ping test and update the result in the GUI."""
        scraper = InternetSpeedScraper()
        speed, ping = scraper.get_internet_speed_and_ping()
        download_speed, upload_speed = scraper.run_speedtest()
        jitter, packet_loss = scraper.get_ping_with_jitter_and_loss()
        self.progress.stop()
        if speed and ping:
            self.result_label.config(text=f"Download: {download_speed:.2f} Mbps, Upload: {upload_speed:.2f} Mbps, Ping: {ping} ms, Jitter: {jitter} ms, Packet Loss: {packet_loss:.2f}%")
            scraper.save_result(speed, ping)
            notify_user("Speed Test Complete", f"Download: {download_speed:.2f} Mbps, Upload: {upload_speed:.2f} Mbps, Ping: {ping} ms, Jitter: {jitter} ms, Packet Loss: {packet_loss:.2f}%")
        else:
            self.result_label.config(text="Failed to retrieve the internet speed or ping.")
            notify_user("Speed Test Failed", "Could not retrieve the speed or ping.")
        self.update_weather()

    def toggle_dark_mode(self):
        """Toggle between light and dark mode."""
        self.style.theme_use('clam')
        self.style.configure("TFrame", background="black")
        self.style.configure("TLabel", background="black", foreground="white")
        self.style.configure("TButton", background="black", foreground="white")

    def fetch_weather(self, city=None, api_key='128080fedfe76dab7a2507e1de71bdcf'):
        """Fetch the current weather for a city."""
        city = city or auto_detect_location()
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            temp = data['main']['temp']
            weather = data['weather'][0]['description']
            return f"{city}: {temp}°C, {weather}"
        else:
            return "Weather data not available."

    def update_weather(self):
        """Update the weather information in the GUI."""
        city = auto_detect_location()
        weather_info = self.fetch_weather(city=city)
        self.weather_label.config(text=weather_info)

    def export_results_to_csv(self):
        """Export the results to a CSV file."""
        with open('results.json', 'r') as file:
            results = [json.loads(line) for line in file]
        with open('results.csv', 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'speed', 'ping']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                writer.writerow(result)
        notify_user("Export Complete", "Results have been exported to results.csv")

    def schedule_test(self):
        """Schedule the speed test to run every hour."""
        schedule.every(1).hours.do(self.run_speed_test)

        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(1)

        threading.Thread(target=run_scheduler, daemon=True).start()

# Create the main window
if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedTestApp(root)
    app.update_weather()  # Update the weather on startup
    root.mainloop()
