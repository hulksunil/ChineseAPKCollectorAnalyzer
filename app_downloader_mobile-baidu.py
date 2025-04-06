from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import os
import json
import re


# This script downloads APK files from the chinese web site mobile.baidu using Selenium.
# It uses the Chrome web driver to automate the browser and download the APK files.
# The script searches for apps using a list of search terms and downloads the APK files if they are not already downloaded which is verified in a downloaded_apps.json file.
# The script also checks the size of the APK files and skips downloading if the size is greater than 400 MB.

downloaded_apps_file = "downloaded_apps.json"
search_terms = ["ai", "chat gpt", "deepseek", "whatsapp", "facebook", "instagram", "tiktok", "snapchat", "twitter", "zoom", "microsoft teams", "google meet", "spotify", "youtube", "netflix", "amazon", "ebay", "aliexpress", "uber", "lyft", "airbnb", "booking", "expedia", "weather", "calculator", "dictionary", "translator", "photo editor", "video editor", "pdf reader", "file manager", "music player", "fitness tracker", "health app", "meditation", "news", "finance", "banking", "stock market", "crypto wallet", "games", "puzzle", "racing", "strategy", "education", "language learning", "kids", "shopping", "food delivery", "recipe", "travel guides", "calendar", "notes", "reminder", "task manager", "email", "browser", "vpn", "security", "antivirus", "password manager", "cloud storage", "document scanner", "qr code scanner", "barcode scanner", "photo collage", "photo filters", "video downloader", "video streaming", "music streaming", "audio recorder", "voice changer", "podcast player", "radio", "weather radar", "stock tracker", "budget planner", "expense tracker", "investment", "crypto trading", "fitness", "step counter", "calorie counter", "meal planner", "diet tracker", "yoga", "workout", "running tracker", "cycling tracker", "sleep tracker", "pregnancy tracker", "baby monitor", "parenting", "school", "homework helper", "exam", "language translator", "grammar checker", "writing assistant", "ebook reader", "audiobook player", "comic reader", "manga reader", "drawing", "painting", "animation", "3d modeling", "photo retouching", "video effects", "video editing tools", "music composition", "dj", "karaoke", "sound effects", "sound mixer", "equalizer", "file sharing", "file compression", "file recovery", "disk cleaner", "system optimizer", "battery saver", "cpu monitor", "ram cleaner", "network analyzer", "wifi manager", "bluetooth manager", "smart home", "home automation", "remote control", "tv", "streaming", "movie", "sports", "live scores", "fantasy sports", "betting", "travel planner", "currency converter", "language dictionary", "local guides", "city maps", "navigation", "gps tracker", "car rental", "flight booking", "train booking", "bus booking", "hotel booking", "restaurant finder", "food recipes", "cooking tips", "kitchen timer", "grocery list", "shopping deals", "discount", "coupon", "cashback", "loyalty", "gift card", "event planner", "ticket booking", "concert", "festival", "party planner", "wedding planner", "birthday", "anniversary", "holiday planner", "seasonal", "gardening", "plant care", "pet care", "dog training", "cat care", "bird watching", "wildlife", "fishing", "hunting", "camping", "hiking", "climbing", "biking", "skiing", "snowboarding", "surfing", "diving", "sailing", "boating", "car maintenance", "car diagnostics", "fuel tracker", "parking", "traffic", "road trip planner", "public transport", "ride sharing", "carpooling", "electric vehicles", "charging stations", "green", "sustainability", "recycling", "energy saver", "water tracker", "carbon footprint", "eco-friendly", "volunteering", "charity", "donation", "fundraising", "community", "social networking", "dating", "friendship",
                "group chat", "video chat", "live streaming", "virtual reality", "augmented reality", "3d games", "multiplayer games", "board games", "card games", "arcade games", "action games", "adventure games", "role-playing games", "simulation games", "sports games", "educational games", "brain training", "memory games", "logic puzzles", "word games", "trivia games", "quiz", "math games", "science", "history", "geography", "art", "music", "coding", "programming tools", "developer tools", "design tools", "photo", "video", "audio", "productivity", "business", "enterprise", "team collaboration", "project management", "time tracking", "crm", "erp", "hr", "payroll", "accounting", "tax", "legal", "contract management", "document management", "presentation tools", "spreadsheet", "word processing", "note-taking", "mind mapping", "idea generation", "brainstorming", "whiteboard", "remote work", "freelancing", "gig", "job search", "career", "resume builder", "interview prep", "networking", "mentorship", "learning", "online courses", "certification", "test prep", "mock tests", "study planner", "study groups", "research tools", "reference", "encyclopedia", "library", "archive", "historical", "cultural", "language", "translation tools", "speech recognition", "voice assistants", "smart assistants", "home assistants", "robotics", "automation tools", "iot", "wearable", "health monitoring", "medical", "doctor", "hospital", "pharmacy", "medicine tracker", "symptom checker", "first aid", "emergency", "disaster management", "weather alerts", "news alerts", "breaking news", "live news", "local news", "international news", "politics", "economy", "business news", "market news", "sports news", "entertainment news", "celebrity news", "gossip", "fashion", "beauty", "makeup", "hairstyle", "skincare", "wellness", "spa", "salon", "nail art", "tattoo", "piercing", "jewelry", "accessory", "clothing", "shoes", "bags", "watches", "luxury", "budget", "thrift", "second-hand", "auction", "bidding", "marketplace", "classifieds", "real estate", "property", "home buying", "home selling", "home renting", "apartment", "house", "villa", "land", "construction", "renovation", "interior design", "furniture", "decor", "lighting", "surveillance", "alarm", "lock", "key", "access control", "identity", "authentication", "biometric", "face recognition", "fingerprint", "iris", "voice", "signature", "document", "contract", "agreement", "policy", "compliance", "audit", "inspection", "quality", "safety", "risk", "insurance", "claims", "policyholder", "agent", "broker", "underwriting", "portfolio", "wealth", "retirement", "pension", "savings", "budgeting", "financial planning", "tax planning", "estate planning", "inheritance", "will", "trust", "lawyer", "court", "case", "trial", "verdict", "appeal", "litigation", "arbitration", "mediation", "settlement", "dispute", "conflict", "resolution", "peace", "harmony", "unity", "diversity", "inclusion", "equality", "justice", "freedom", "rights", "advocacy", "activism", "campaign", "movement", "protest", "petition", "vote", "election", "democracy", "government", "legislation", "regulation", "actuarial"]


def load_downloaded_apps():
    if os.path.exists(downloaded_apps_file):
        with open(downloaded_apps_file, "r") as file:
            return set(json.load(file))
    return set()


def save_downloaded_apps(downloaded_apps):
    with open(downloaded_apps_file, "w") as file:
        json.dump(list(downloaded_apps), file)


downloaded_apps = load_downloaded_apps()


def get_app_size(current_app):
    """
    Gets the app size of the current app in MB
    """
    app_size = None

    size_str = current_app.find_element(
        By.CLASS_NAME, "normal-app-size").text
    match = re.match(r"(\d+\.?\d*)\s*(KB|MB|GB)",
                     size_str, re.IGNORECASE)

    if match:
        size_value = float(match.group(1))
        size_unit = match.group(2).upper()
        print("Size:", size_value, size_unit)

        unit_multipliers = {
            "KB": 1 / 1024,
            "MB": 1,
            "GB": 1024
        }

        app_size = size_value * unit_multipliers[size_unit]
    return app_size


def click_download_btn(driver):
    """
    Clicks the download button on the app page
    This method checks for both single and double download buttons so it clicks the right one
    """
    double_download_btns = driver.find_elements(
        By.CSS_SELECTOR, ".c-btn.double-btn-item.c-btn--primary")

    if len(double_download_btns) > 0:
        double_download_btns[1].click()  # click download button
    else:
        single_download_btn = driver.find_element(
            By.CLASS_NAME, "business-btn")
        single_download_btn.click()  # click download button
    print(f"Downloading ...")


def wait_for_downloads_to_complete(download_dir, timeout=60):
    """
    Waits for downloads to finish
    This method checks the download directory for any files with the ".crdownload" extension, which indicates that a download is in progress.
    """
    seconds = 0
    hasPrintedMessage = False
    while any(fname.endswith(".crdownload") for fname in os.listdir(download_dir)):
        if not hasPrintedMessage:
            print("Waiting for download to finish...")
            hasPrintedMessage = True
        time.sleep(2)
        seconds += 2

        if seconds % (timeout*0.25) == 0 or seconds % (timeout*0.25) == 1:
            print(f"Waiting for {seconds} seconds...")

        if seconds > timeout:
            print("Timeout reached while waiting for download.")
            break


def download_apk(download_dir="downloads"):
    """
    The main method to download APK files
    """

    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": os.path.abspath(download_dir)}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options)

    try:
        for search_term in search_terms:
            print("Searching for apps with term: ", search_term)
            search_term.replace(" ", "%20")

            driver.get("https://mobile.baidu.com/search?w=" + search_term)

            time.sleep(1)

            all_apps_len = len(driver.find_elements(
                By.CLASS_NAME, "normal-app-content"))
            goto_url = driver.current_url
            print(f"Found {all_apps_len} apps.")
            time.sleep(1)

            for i in range(all_apps_len):
                current_app = driver.find_elements(
                    By.CLASS_NAME, "normal-app-content")[i]
                print("Inspecting app #", str(i+1))
                app_name = current_app.find_element(
                    By.CLASS_NAME, "normal-app-title").text
                print("App name: ", app_name)
                app_size = get_app_size(current_app)

                if app_name in downloaded_apps:
                    print("App already downloaded. Skipping...")
                    continue

                if app_size is not None and app_size > 400:
                    print("App size is greater than 400 MB. Skipping...")
                    continue

                current_app.click()
                time.sleep(4)  # wait for app page to load

                click_download_btn(driver)

                # add app to downloaded apps list
                downloaded_apps.add(app_name)
                save_downloaded_apps(downloaded_apps)

                # let the download start and ad popup, then go back to the search results page
                time.sleep(1)

                # go back to the search results page so we can click on the next app
                driver.get(goto_url)
                time.sleep(2)

    except Exception as e:
        print(f"Error downloading : {e}")
    finally:
        wait_for_downloads_to_complete(download_dir)
        print("Closing browser...")
        driver.quit()


if __name__ == "__main__":
    download_apk()
    print("Download complete.")
