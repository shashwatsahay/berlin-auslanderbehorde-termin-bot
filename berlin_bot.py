import time
import os
import logging
from platform import system

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.chrome.service import Service

system = system()

logging.basicConfig(
    format='%(asctime)s\t%(levelname)s\t%(message)s',
    level=logging.INFO,
)

class WebDriver:
    def __init__(self):
        self._driver: webdriver.Chrome
        self._implicit_wait_time = 10

    def __enter__(self) -> webdriver.Chrome:
        logging.info("Open browser")
        # some stuff that prevents us from being locked out
        homedir = os.path.expanduser("~")
        webdriver_service=os.path.join(os.getcwd(), "chromedriver_win32\chromedriver.exe")
        options = webdriver.ChromeOptions() 
        options.add_argument('--disable-blink-features=AutomationControlled')
        self._driver = webdriver.Chrome(executable_path=webdriver_service, options=options)
        self._driver.implicitly_wait(self._implicit_wait_time) # seconds
        self._driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self._driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
        return self._driver

    def __exit__(self, exc_type, exc_value, exc_tb):
        logging.info("Close browser")
        self._driver.quit()

class BerlinBot:
    def __init__(self):
        self.wait_time = 10
        self._sound_file = os.path.join(os.getcwd(), "alarm.wav")
        self._error_message = """Für die gewählte Dienstleistung sind aktuell keine Termine frei! Bitte"""

    @staticmethod
    def enter_start_page(driver: webdriver.Chrome):
        logging.info("Visit start page")
        driver.get("https://otv.verwalt-berlin.de/ams/TerminBuchen")
        WebDriverWait(driver, 100).until(expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="mainForm"]/div/div/div/div/div/div/div/div/div/div[1]/div[1]/div[2]/a')))
        driver.find_element(By.XPATH, '//*[@id="mainForm"]/div/div/div/div/div/div/div/div/div/div[1]/div[1]/div[2]/a').click()
        # time.sleep(5)

    @staticmethod
    def tick_off_some_bullshit(driver: webdriver.Chrome):
        logging.info("Ticking off agreement")
        WebDriverWait(driver, 100).until(expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="xi-div-1"]/div[4]/label[2]/p')))
        driver.find_element(By.XPATH, '//*[@id="xi-div-1"]/div[4]/label[2]/p').click()
        WebDriverWait(driver, 100).until(expected_conditions.presence_of_element_located((By.ID, 'applicationForm:managedForm:proceed')))
        driver.find_element(By.ID, 'applicationForm:managedForm:proceed').click()
        # time.sleep(5)

    @staticmethod
    def enter_form(driver: webdriver.Chrome):
        logging.info("Fill out form")
        # select china
        WebDriverWait(driver, 100).until(expected_conditions.presence_of_element_located((By.ID, 'xi-sel-400')))
        s = Select(driver.find_element(By.ID, 'xi-sel-400'))
        s.select_by_visible_text("Indien")
        time.sleep(2)
        # eine person
        WebDriverWait(driver, 100).until(expected_conditions.presence_of_element_located((By.ID, 'xi-sel-422')))
        s = Select(driver.find_element(By.ID, 'xi-sel-422'))
        s.select_by_visible_text("eine Person")
        time.sleep(2)
        # no family
        WebDriverWait(driver, 100).until(expected_conditions.presence_of_element_located((By.ID, 'xi-sel-427')))
        s = Select(driver.find_element(By.ID, 'xi-sel-427' ))
        s.select_by_visible_text("ja")
        time.sleep(2)
        WebDriverWait(driver, 100).until(expected_conditions.presence_of_element_located((By.ID, 'xi-sel-428')))
        s = Select(driver.find_element(By.ID, 'xi-sel-428' ))
        s.select_by_visible_text("Indien")
        time.sleep(2)

        # extend stay
        WebDriverWait(driver, 100).until(expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="xi-div-30"]/div[2]/label/p')))
        driver.find_element(By.XPATH, '//*[@id="xi-div-30"]/div[2]/label/p').click()
        time.sleep(2)

        # click on study group
        WebDriverWait(driver, 100).until(expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="inner-436-0-2"]/div/div[5]/label/p')))
        driver.find_element(By.XPATH, '//*[@id="inner-436-0-2"]/div/div[5]/label/p').click()
        time.sleep(2)

        # b/c of stufy
        WebDriverWait(driver, 100).until(expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="inner-436-0-2"]/div/div[6]/div/div[2]/label')))
        driver.find_element(By.XPATH, '//*[@id="inner-436-0-2"]/div/div[6]/div/div[3]/label').click()
        time.sleep(4)

        # submit form
        # print(expected_conditions.invisibility_of_element((By.CSS_SELECTOR, "div.loading")))

        WebDriverWait(driver, 100).until(expected_conditions.invisibility_of_element((By.CSS_SELECTOR, "div.loading")))
        WebDriverWait(driver, 100).until(expected_conditions.presence_of_element_located((By.ID, 'applicationForm:managedForm:proceed')))
        driver.find_element(By.ID, 'applicationForm:managedForm:proceed').click()
        WebDriverWait(driver, 100).until(expected_conditions.invisibility_of_element((By.CSS_SELECTOR, "div.loading")))
        WebDriverWait(driver, 100).until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        time.sleep(5)
    
    def _success(self):
        logging.info("!!!SUCCESS - do not close the window!!!!")
        while True:
            self._play_sound_osx(self._sound_file)
            time.sleep(30)
        
        # todo play something and block the browser


    def run_once(self):
        with WebDriver() as driver:
            try:
                self.enter_start_page(driver)
                self.tick_off_some_bullshit(driver)
                self.enter_form(driver)
                # retry submit
                for _ in range(30):
                    if "Auswahl Uhrzeit" in driver.page_source or  'Familiäre Gründe' not in driver.page_source:
                        self._success()
                    logging.info("Retry submitting form")
                    if driver.find_elements(By.CSS_SELECTOR, "div.loading"):
                        WebDriverWait(driver, 100).until(expected_conditions.invisibility_of_element((By.CSS_SELECTOR, "div.loading")))
                    flag=True
                    WebDriverWait(driver, 100).until(expected_conditions.presence_of_element_located((By.ID, 'applicationForm:managedForm:proceed')))
                    driver.find_element(By.ID, 'applicationForm:managedForm:proceed').click()
                    if driver.find_elements(By.CSS_SELECTOR, "div.loading"):
                        WebDriverWait(driver, 100).until(expected_conditions.invisibility_of_element((By.CSS_SELECTOR, "div.loading")))
                    WebDriverWait(driver, 100).until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                    time.sleep(2)
            except Exception as e:
                print(e)
                pass

    def run_loop(self):
        # play sound to check if it works
        self._play_sound_osx(self._sound_file)
        while True:
            logging.info("One more round")
            self.run_once()
            time.sleep(self.wait_time)

    # stolen from https://github.com/JaDogg/pydoro/blob/develop/pydoro/pydoro_core/sound.py
    @staticmethod
    def _play_sound_osx(sound, block=True):
        """
        Utilizes AppKit.NSSound. Tested and known to work with MP3 and WAVE on
        OS X 10.11 with Python 2.7. Probably works with anything QuickTime supports.
        Probably works on OS X 10.5 and newer. Probably works with all versions of
        Python.
        Inspired by (but not copied from) Aaron's Stack Overflow answer here:
        http://stackoverflow.com/a/34568298/901641
        I never would have tried using AppKit.NSSound without seeing his code.
        """
        from playsound import playsound
        
        logging.info("Play sound")
        playsound(sound)
        # if "://" not in sound:
        #     if not sound.startswith("/"):
        #         from os import getcwd

        #         sound = getcwd() + "/" + sound
        #     sound = "file://" + sound
        # url = NSURL.URLWithString_(sound)
        # nssound = NSSound.alloc().initWithContentsOfURL_byReference_(url, True)
        # if not nssound:
        #     raise IOError("Unable to load sound named: " + sound)
        # nssound.play()

        # if block:
        #     sleep(nssound.duration())

if __name__ == "__main__":
    BerlinBot().run_loop()
