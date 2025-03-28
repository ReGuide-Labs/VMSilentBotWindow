import os
import math
import random
import time
import threading

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from colorama import Fore, Style  # Add colorama for colored output
global_block_index = 0 

def log(profile, message, logger=None, color=Fore.RESET):
    """Log messages using the provided logger or print to console with color."""
    log_message = f"{color}[Profile: {profile}] {message}{Style.RESET_ALL}"
    if logger:
        logger.info(log_message)
    else:
        print(log_message)

def contribute(silent_jwt, profile):

    project_dir = os.path.dirname(os.path.abspath(__file__))
    profile_path = os.path.join(project_dir, 'profiles', profile)

    if not os.path.exists(profile_path):
        os.makedirs(profile_path)

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.88 Safari/537.36"

    options = Options()
    # options.add_argument("--headless=new")
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--user-agent={user_agent}")
    options.add_argument("--disable-infobars")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    chromedriver_path = os.path.join(project_dir, "chromium", "chromedriver.exe")
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
        """
    })

    driver.get("https://ceremony.silentprotocol.org/")

    driver.execute_script(f"window.localStorage.setItem('silent_jwt', '{silent_jwt}');")

    driver.get("https://ceremony.silentprotocol.org/ceremonies")
    log(profile, "Successfully opened page and set silent_jwt.")

    return driver

class presence_of_any_element_located:
    def __init__(self, locator1, locator2):
        self.locator1 = locator1
        self.locator2 = locator2

    def __call__(self, driver):
        found_elem1 = None
        found_elem2 = None
        try:
            found_elem1 = driver.find_element(*self.locator1)
        except:
            pass

        try:
            found_elem2 = driver.find_element(*self.locator2)
        except:
            pass

        if found_elem1:
            return ('xpath1', found_elem1)

        if found_elem2:
            return ('xpath2', found_elem2)

        return False
    
def automation_interact(driver, profile, interval=10, logger=None, on_reset=None):

    wait = WebDriverWait(driver, 60)

    while True:
        try:
            wait_xpath = '//*[@id="__next"]/div[1]/div[2]/div[2]/p[1]'
            ogps_earned_xpath = '//*[@id="__next"]/main/div/div[1]/h6[1]'
            which_xpath, found_element = wait.until(
                presence_of_any_element_located(
                    (By.XPATH, wait_xpath),
                    (By.XPATH, ogps_earned_xpath)
                )
            )            
            if which_xpath == 'xpath1':
                text_wait = found_element.text.lower()
                print("Element wait_xpath appeared first:", found_element.text)
            else:
                text_ogp = found_element.text.lower()
                print("Element ogps_earned_xpath appeared first:", found_element.text)
            if "ogps" in text_ogp or "your time" not in text_wait:
                log(profile, "Text 'OGPs earned' found or exited queue, starting button search.", logger, color=Fore.GREEN)

                button_found = False
                max_blocks = 10

                # Dựa vào chỉ số toàn cục để bắt đầu block
                for offset in range(max_blocks):
                    i = (global_block_index + offset) % max_blocks + 1  # 1-based index

                    block_xpath = f'//*[@id="__next"]/main/div/div[2]/div[{i}]'
                    try:
                        element = driver.find_element(By.XPATH, block_xpath)
                        log(profile, f"Found block {i}: {element.text}", logger, color=Fore.GREEN)

                        button_xpath = f'{block_xpath}/div[2]/div[2]/button'
                        try:
                            button_element = driver.find_element(By.XPATH, button_xpath)
                            button_element.click()
                            log(profile, f"Clicked button in block {i}.", logger, color=Fore.GREEN)

                            time.sleep(30)

                            continue_button_xpath = '//*[@id="__next"]/div[1]/div[2]/div[3]/button'
                            try:
                                continue_button = driver.find_element(By.XPATH, continue_button_xpath)
                                if "continue" in continue_button.text.lower():
                                    log(profile, "Continue button found. Starting random mouse move...", logger, color=Fore.GREEN)
                                    perform_random_interactions_and_submit(driver, profile, logger)
                                    button_found = True
                                    global_block_index = (i % max_blocks)  # cập nhật cho profile tiếp theo
                                    break
                                else:
                                    log(profile, "Continue button not valid.", logger, color=Fore.YELLOW)

                            except:
                                log(profile, "Continue button not found.", logger, color=Fore.YELLOW)
                                continue

                        except Exception:
                            log(profile, f"Block {i} already contributed or button not clickable. Skipping...", logger, color=Fore.RED)
                            continue

                    except:
                        continue

                if not button_found:
                    log(profile, "No button found, reloading the page.", logger, color=Fore.RED)
                    driver.get("https://ceremony.silentprotocol.org/ceremonies")
                    continue

            else:
                input_xpath = '//*[@id="__next"]/div[1]/main/div/div[1]/div[1]/input'
                try:
                    driver.find_element(By.XPATH, input_xpath)
                    log(profile, "Input found, reloading.", logger, color=Fore.GREEN)
                    driver.get("https://ceremony.silentprotocol.org/ceremonies")
                    continue
                except:
                    log(profile, "Input not found. Checking exit or success...", logger, color=Fore.RED)        
                    
        except Exception as e:
            log(profile, "Not ready - 'OGPs earned' not found or still in queue.", logger, color=Fore.RED)

            bind_xpath = '//*[@id="__next"]/div[1]/div[2]/div[2]/div/div'
            try:
                bind_element = driver.find_element(By.XPATH, bind_xpath)
                bind_text = bind_element.text.lower()
                log(profile, f"Bind text found: {bind_text}", logger, color=Fore.GREEN)
                
                if "you are behind" in bind_text:
                    queue_number = int(''.join(filter(str.isdigit, bind_text.split("behind")[1])))
                    log(profile, f"Queue number extracted: {queue_number}", logger, color=Fore.GREEN)
                    
                    if queue_number > 200:
                        log(profile, "Queue number exceeds 200 -> Quitting driver.", logger, color=Fore.RED)
                        driver.quit()
                        if on_reset:
                            on_reset()
                        break
            except:
                log(profile, "Bind text not found or unable to check queue number.", logger, color=Fore.RED)
            try:
                success_text_xpath = '//*[@id="__next"]/div[1]/div[2]/div[2]'
                proccessed_text_xpath = '//*[@id="__next"]/div[1]/div[2]/div/p'
                success_text_element = None
                proccessed_text_element = None

                try:
                    success_text_element = driver.find_element(By.XPATH, success_text_xpath)
                except:
                    pass

                try:
                    proccessed_text_element = driver.find_element(By.XPATH, proccessed_text_xpath)
                except:
                    pass

                if success_text_element and "successfully uploaded" in success_text_element.get_attribute('innerText'):
                    log(profile, "Successfully exited or uploaded.", logger, color=Fore.GREEN)
                    driver.quit()
                    if on_reset:
                        on_reset()
                    break

                if proccessed_text_element and "processed" in proccessed_text_element.get_attribute('innerText').lower():
                    log(profile, "Processed text found, exiting driver.", logger, color=Fore.GREEN)
                    driver.quit()
                    if on_reset:
                        on_reset()
                    break
            except:
                log(profile, "Did not find 'successfully uploaded'. Waiting 30s...", logger, color=Fore.RED)
                
            if "no such window" in str(e).lower() or "unable to evaluate script" in str(e).lower():
                log(profile, "Driver is closed -> Break automation_interact.", logger, color=Fore.RED)
                break
            log(profile, f"Error while checking queue: {e}", logger, color=Fore.RED)

        time.sleep(interval)
        
def perform_random_interactions_and_submit(driver, profile, logger=None):
    end_time = time.time() + 5
    while time.time() < end_time:
        rand_index = random.randint(1, 1680)
        random_xpath = f'//*[@id="__next"]/div[1]/div[2]/div[1]/div[{rand_index}]'
        try:
            random_element = driver.find_element(By.XPATH, random_xpath)
            ActionChains(driver).move_to_element(random_element).perform()
        except:
            pass
        time.sleep(0.1)

    continue_button_xpath = '//*[@id="__next"]/div[1]/div[2]/div[3]/button'
    continue_button = driver.find_element(By.XPATH, continue_button_xpath)
    continue_button.click()
    log(profile, "Successfully clicked Continue.", logger, color=Fore.GREEN)
    time.sleep(2)

    input_xpath = '//*[@id="__next"]/div[1]/main/div/div[1]/div[1]/input'
    input_element = driver.find_element(By.XPATH, input_xpath)
    random_text = ''.join(random.choices(
        'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=10
    ))
    log(profile, f"Entered random text: {random_text}", logger, color=Fore.GREEN)
    input_element.send_keys(random_text)
    time.sleep(2)
    final_button_xpath = '//*[@id="__next"]/div[1]/main/div/div[2]/button[1]'
    final_button = driver.find_element(By.XPATH, final_button_xpath)
    final_button.click()
    log(profile, "Successfully clicked final button.", logger, color=Fore.GREEN)
    

def run_profile(profile, silent_jwt, index, columns, rows, window_width, window_height, logger, on_reset=None):
    """Run on each thread, initialize driver, set window position/size, then automate."""
    driver = contribute(silent_jwt, profile)

    row = index // columns
    col = index % columns
    x = col * window_width
    y = row * window_height

    driver.set_window_position(x, y)
    driver.set_window_size(window_width, window_height)
    log(profile, f"Window positioned at ({x},{y}), size = {window_width}x{window_height}", logger, color=Fore.GREEN)

    automation_interact(driver, profile, logger=logger, on_reset=on_reset)


def run_profiles(profiles, silent_jwt, logger=None, on_reset=None):

    screen_width = 1920
    screen_height = 1080
    print(f"Using default screen size: {screen_width}x{screen_height}")

    total = 5
    columns = math.ceil(math.sqrt(total))
    rows = math.ceil(total / columns)

    SCALE = 0.8
    scaled_width = int(screen_width * SCALE)
    scaled_height = int(screen_height * SCALE)

    window_width = scaled_width // columns
    window_height = scaled_height // rows

    threads = []
    for i, profile in enumerate(profiles):
        t = threading.Thread(
            target=run_profile,
            args=(profile, silent_jwt, i, columns, rows, window_width, window_height, logger)
        )
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
