import os
import time
import random
import datetime
import sys # Needed for flushing
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- REAL-TIME CONFIG ---
THREADS = 2           
BURST_SIZE = 8        
BURST_DELAY = 0.05    
CYCLE_DELAY = 1.0     
LOG_FILE = "message_log.txt"

def log_heartbeat(agent_id, count, start_time):
    elapsed = time.time() - start_time
    if elapsed == 0: elapsed = 1
    
    speed = count / elapsed
    timestamp = datetime.datetime.now().strftime("%H:%M:%S") # Short time format
    
    # The Log Line
    log_entry = f"[{timestamp}] ⚡ Agent {agent_id} | Total: {count} | Speed: {speed:.1f} msg/s"
    
    # FORCE PRINT TO CONSOLE INSTANTLY
    print(log_entry, flush=True)
    
    try:
        with open(LOG_FILE, "a") as f:
            f.write(log_entry + "\n")
    except:
        pass

def setup_driver(agent_id):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    chrome_options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/12{agent_id+5}.0.0.0 Safari/537.36")
    return webdriver.Chrome(options=chrome_options)

def instant_inject(driver, element, text):
    driver.execute_script("""
        var elm = arguments[0], txt = arguments[1];
        elm.focus();
        document.execCommand('insertText', false, txt);
        elm.dispatchEvent(new Event('input', {bubbles: true}));
    """, element, text)

def agent_worker(agent_id, session_id, target_input, messages):
    print(f"🚀 [Agent {agent_id}] Real-Time Engine Started...", flush=True)
    driver = setup_driver(agent_id)
    start_time = time.time()
    
    try:
        driver.get("https://www.instagram.com/")
        
        clean_session = session_id
        if "sessionid=" in session_id:
            try: clean_session = session_id.split("sessionid=")[1].split(";")[0]
            except: pass
            
        driver.add_cookie({'name': 'sessionid', 'value': clean_session, 'domain': '.instagram.com', 'path': '/'})
        driver.refresh()
        time.sleep(5)

        driver.get(f"https://www.instagram.com/direct/t/{target_input}/")
        time.sleep(5)
        
        box_xpath = "//div[@contenteditable='true']"
        try:
            msg_box = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, box_xpath))
            )
        except:
            print(f"❌ [Agent {agent_id}] UI Fail.", flush=True)
            return

        total_sent = 0
        while True:
            try:
                for i in range(BURST_SIZE):
                    msg = random.choice(messages)
                    jitter = "⠀" * random.randint(0, 1)
                    instant_inject(driver, msg_box, f"{msg}{jitter}")
                    msg_box.send_keys(Keys.ENTER)
                    
                    total_sent += 1
                    time.sleep(BURST_DELAY)
                
                log_heartbeat(agent_id, total_sent, start_time)
                time.sleep(CYCLE_DELAY)

                if total_sent % 40 == 0:
                    try: msg_box = driver.find_element(By.XPATH, box_xpath)
                    except: pass

            except Exception:
                print(f"⚠️ [Agent {agent_id}] Refreshing...", flush=True)
                driver.refresh()
                time.sleep(5)
                start_time = time.time() # Reset speed calc
                total_sent = 0
                try:
                    msg_box = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.XPATH, box_xpath))
                    )
                except:
                    break
    except Exception:
        pass
    finally:
        driver.quit()

def main():
    print(f"🔥 V17.6 REAL-TIME LOGGING ENABLED | {THREADS} AGENTS", flush=True)
    
    session_id = os.environ.get("INSTA_SESSION", "").strip()
    target_input = os.environ.get("TARGET_THREAD_ID", "").strip()
    messages = os.environ.get("MESSAGES", "Hello").split("|")

    if not session_id: return

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for i in range(THREADS):
            executor.submit(agent_worker, i+1, session_id, target_input, messages)

if __name__ == "__main__":
    main()
