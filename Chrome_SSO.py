

# # ---------------------------------------ALL PLATFORMS [Windows, MacOS, Linux]----------------------------------------

import os
import logging
import tempfile
import platform
import subprocess
from enum import Enum
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException


class OperatingSystem(Enum):
    WINDOWS = "Windows"
    LINUX = "Linux"
    MACOS = "Darwin"


class SSO:
    def __init__(self, user_data_dir):
        self.logger = None
        self.driver = None
        self.user_data_dir = user_data_dir

    def setupLogger(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def runChromeWithDebugging(self):
        system = platform.system()
        if system in (OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value, OperatingSystem.MACOS.value):
            command = f"cmd.exe /c start chrome.exe --remote-debugging-port=9988 --user-data-dir={self.user_data_dir}" if system == OperatingSystem.WINDOWS.value else \
                      f"google-chrome --remote-debugging-port=9988 --user-data-dir={self.user_data_dir}" if system == OperatingSystem.LINUX.value else \
                      f"open -na 'Google Chrome' --args --remote-debugging-port=9988 --user-data-dir={self.user_data_dir}"
            try:
                subprocess.run(command, shell=True, check=True)
                self.logger.info('Chrome started with remote debugging.')
            except subprocess.CalledProcessError as e:
                self.logger.error(f'Command failed with exit code: {e.returncode}')
        else:
            raise Exception("Unsupported operating system")

    def setupChromeDriver(self):
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_experimental_option("debuggerAddress", "localhost:9988")

        try:
            self.logger.info(ChromeDriverManager().install())
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chromeOptions)
            self.driver.maximize_window()
            self.logger.info('Chrome WebDriver set up successfully.')
        except (WebDriverException, NoSuchElementException, TimeoutException) as e:
            self.logger.error(f'Error setting up Chrome WebDriver: {str(e)}')

    def automateChrome(self):
        if self.driver is not None:
            url = "https://issues-pdx.amazon.com/issues/bulk-create"
            self.driver.get(url)

    def closeBrowser(self):
        if self.driver is not None:
            self.driver.quit()
            self.logger.info('Chrome WebDriver closed.')


def getUserDataDir():
    base_user_data_dir = os.path.join(tempfile.gettempdir(), 'SSO')
    user_data_dir_path = os.path.join(base_user_data_dir, 'SSO')

    if not os.path.exists(base_user_data_dir):
        os.makedirs(base_user_data_dir, exist_ok=True)

    return user_data_dir_path


def main():
    user_data_dir_path = getUserDataDir()
    automation = SSO(user_data_dir_path)
    automation.setupLogger()
    automation.runChromeWithDebugging()
    automation.setupChromeDriver()
    automation.automateChrome()
    automation.closeBrowser()


if __name__ == "__main__":
    main()


