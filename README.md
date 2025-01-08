## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

# Internet Speed Test GUI

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Selenium](https://img.shields.io/badge/Selenium-4.0-green)
![Tkinter](https://img.shields.io/badge/Tkinter-4.0-green)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4.10-brightgreen)

## Overview

This project is a simple GUI application to test your internet speed using Selenium and BeautifulSoup. The GUI is built using Tkinter, and the speed test is run via [fast.com](https://fast.com).

## Features
- **Easy-to-use** GUI with a "Start Test" button.
- **Progress bar** to indicate the speed test is running.
- **Real-time** speed display after the test completes.
- **Headless** mode execution for faster performance.

<h1 align="center">
  <img src="img.png" width="300" height="80" alt="Sidiq Olasode aka JSX">
</h1>

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/sidiq20/scrapedfast.com.git
    cd scrapedfast.com
    ```

2. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the application:
    ```bash
    python main.py
    ```

## Building the Executable

To create an executable, use `pyinstaller`:
```bash
pyinstaller --onefile --noconsole main.py





