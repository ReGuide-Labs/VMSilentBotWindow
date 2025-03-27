import os
import math
import random
import time
import threading
import ctypes

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def log(profile, message):
    print(f"[Profile: {profile}] {message}")


def contribute(silent_jwt, profile):

    project_dir = os.path.dirname(os.path.abspath(__file__))
    profile_path = os.path.join(project_dir, 'profiles', profile)

    if not os.path.exists(profile_path):
        os.makedirs(profile_path)

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.88 Safari/537.36"

    options = Options()
    options.add_argument("--headless=new")
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
    log(profile, "Đã mở trang và thiết lập silent_jwt thành công.")

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
    
def automation_interact(driver, profile, interval=10):

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
                print("Element wait_xpath đã xuất hiện trước:", found_element.text)
            else:
                text_ogp = found_element.text.lower()
                print("Element ogps_earned_xpath đã xuất hiện trước:", found_element.text)
            if "ogps" in text_ogp or "your time" not in text_wait:
                log(profile, "Text 'OGPs earned' found hoặc đã thoát queue, bắt đầu tìm button.")

                button_clicked = False
                for i in range(1, 11):
                    block_xpath = f'//*[@id="__next"]/main/div/div[2]/div[{i}]'
                    try:
                        element = driver.find_element(By.XPATH, block_xpath)
                        log(profile, f"Tìm thấy block {i}: {element.text}")

                        button_xpath = f'//*[@id="__next"]/main/div/div[2]/div[{i}]/div[2]/div[2]/button'
                        span_xpath = f'//*[@id="__next"]/main/div/div[2]/div[{i}]/div[2]/div[2]/span/div'

                        try:
                            button_element = wait.until(
                                EC.element_to_be_clickable((By.XPATH, button_xpath))
                            )
                            button_element.click()
                            log(profile, f"Đã click button ở block {i}.")
                            button_clicked = True

                            continue_button_xpath = '//*[@id="__next"]/div[1]/div[2]/div[3]/button'
                            continue_button = wait.until(
                                EC.element_to_be_clickable((By.XPATH, continue_button_xpath))
                            )

                            if "continue" in continue_button.text.lower():
                                log(profile, "Continue button found. Bắt đầu random mouse move...")

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

                                continue_button.click()
                                log(profile, "Đã click Continue.")
                                time.sleep(2)

                                input_xpath = '//*[@id="__next"]/div[1]/main/div/div[1]/div[1]/input'
                                input_element = wait.until(
                                    EC.presence_of_element_located((By.XPATH, input_xpath))
                                )
                                random_text = ''.join(random.choices(
                                    'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=10
                                ))
                                input_element.send_keys(random_text)
                                log(profile, f"Nhập text ngẫu nhiên: {random_text}")

                                final_button_xpath = '//*[@id="__next"]/div[1]/main/div/div[2]/button[1]'
                                final_button = wait.until(
                                    EC.element_to_be_clickable((By.XPATH, final_button_xpath))
                                )
                                final_button.click()
                                log(profile, "Đã click final button.")

                        except Exception as e:
                            log(profile, f"Lỗi click button ở block {i}: {e}")

                        try:
                            span_element = driver.find_element(By.XPATH, span_xpath)
                            log(profile, f"Span ở block {i}: {span_element.text}")
                        except:
                            pass

                    except:
                        pass

                if not button_clicked:
                    log(profile, "Không tìm thấy button nào, reload trang.")
                    driver.get("https://ceremony.silentprotocol.org/ceremonies")
                    continue

            else:
                log(profile, "Chưa sẵn sàng - Chưa có 'OGPs earned' hoặc vẫn trong queue.")

                input_xpath = '//*[@id="__next"]/div[1]/main/div/div[1]/div[1]/input'
                try:
                    driver.find_element(By.XPATH, input_xpath)
                    log(profile, "Tìm thấy input, reload.")
                    driver.get("https://ceremony.silentprotocol.org/ceremonies")
                    continue
                except:
                    log(profile, "Không thấy input. Kiểm tra exit hoặc success...")

                exit_button_xpath = '//*[@id="__next"]/div[1]/div[2]/div/button'
                try:
                    exit_button = driver.find_element(By.XPATH, exit_button_xpath)
                    exit_button.click()
                    log(profile, "Click Exit button -> Quit driver.")
                    driver.quit()
                    break
                except:
                    log(profile, "Không thấy Exit button, kiểm tra 'successfully uploaded'.")

                try:
                    success_text_xpath = '//*[@id="__next"]/div[1]/div[2]/div[2]'
                    success_text_element = driver.find_element(By.XPATH, success_text_xpath)
                    if "successfully uploaded" in success_text_element.get_attribute('innerText'):
                        log(profile, "'successfully uploaded' -> Quit driver.")
                        driver.quit()
                        break
                except:
                    log(profile, "Chưa thấy 'successfully uploaded'. Chờ 30s...")

        except Exception as e:
            if "no such window" in str(e).lower() or "unable to evaluate script" in str(e).lower():
                log(profile, "Driver is closed -> Break automation_interact.")
                break
            log(profile, f"Đang kiểm tra hàng chờ queue...")

        time.sleep(interval)


def run_profile(profile, silent_jwt, index, columns, rows, window_width, window_height):
    """Hàm chạy trên mỗi luồng, khởi tạo driver, set vị trí/kích thước cửa sổ, rồi automation."""
    driver = contribute(silent_jwt, profile)

    row = index // columns
    col = index % columns
    x = col * window_width
    y = row * window_height

    driver.set_window_position(x, y)
    driver.set_window_size(window_width, window_height)
    log(profile, f"Cửa sổ đặt tại ({x},{y}), size = {window_width}x{window_height}")

    automation_interact(driver, profile)


def run_profiles(profiles, silent_jwt):

    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()

    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)
    print(f"Detected screen size: {screen_width}x{screen_height}")

    total = 10
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
            args=(profile, silent_jwt, i, columns, rows, window_width, window_height)
        )
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
