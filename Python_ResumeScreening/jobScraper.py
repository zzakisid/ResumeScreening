from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_driver_path = (
    r"D:\PythonProject\Python_ResumeScreening\chromedriver-win64\chromedriver.exe"
)

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
)
options.add_experimental_option("excludeSwitches", ["enable-automation"])

service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

driver.execute_script(
    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
)

job_site_url = "https://www.linkedin.com/jobs/search/?keywords=software%20engineer"
driver.get(job_site_url)

WebDriverWait(driver, 20).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".base-search-card"))
)

job_data = []
processed_links = set()


def closeLogInPopUp():
    time.sleep(3)
    try:
        body = driver.find_element(By.CSS_SELECTOR, "button.modal__dismiss")
        action = webdriver.ActionChains(driver)
        action.move_to_element_with_offset(body, -2, 0).click().perform()
        print("Attempted to close popup by clicking outside")
        return True
    except Exception as e:
        print(f"Error handling login popup: {e}")
        return False


def clean_description(description):
    return " ".join(description.splitlines())


def collectJobLinks():
    links = []
    job_cards = driver.find_elements(By.CSS_SELECTOR, ".base-search-card")
    for job in job_cards:
        try:
            job_link = job.find_element(
                By.CSS_SELECTOR, "a.base-card__full-link"
            ).get_attribute("href")
            if job_link not in processed_links:
                links.append(job_link)
                processed_links.add(job_link)
        except Exception as e:
            print(f"Error extracting link: {e}")
    return links


def scrapeJobDetails(url):
    try:
        driver.get(url)
        time.sleep(2)

        try:
            title = driver.find_element(By.CSS_SELECTOR, ".top-card-layout__title").text
        except:
            try:
                title = driver.find_element(
                    By.CSS_SELECTOR, ".job-details-jobs-unified-top-card__job-title"
                ).text
            except:
                title = "N/A"

        try:
            company = driver.find_element(
                By.CSS_SELECTOR, ".topcard__org-name-link"
            ).text
        except:
            try:
                company = driver.find_element(
                    By.CSS_SELECTOR, ".job-details-jobs-unified-top-card__company-name"
                ).text
            except:
                company = "N/A"

        try:
            location = driver.find_element(
                By.CSS_SELECTOR, ".topcard__flavor--bullet"
            ).text
        except:
            try:
                location = driver.find_element(
                    By.CSS_SELECTOR, ".job-details-jobs-unified-top-card__bullet"
                ).text
            except:
                location = "N/A"

        try:
            description = driver.find_element(
                By.CSS_SELECTOR, ".description__text"
            ).text
        except:
            try:
                description = driver.find_element(
                    By.CSS_SELECTOR, ".show-more-less-html__markup"
                ).text
            except:
                try:
                    description = driver.find_element(
                        By.CSS_SELECTOR, "#job-details"
                    ).text
                except:
                    description = "N/A"

        description = clean_description(description)

        return {
            "Title": title,
            "Company": company,
            "Location": location,
            "Description": description,
            "Job Link": url,
        }
    except Exception as e:
        print(f"Error scraping job details: {e}")
        return None


closeLogInPopUp()

max_scrolls = 1000
max_jobs = 150

for _ in range(max_scrolls):
    job_links = collectJobLinks()
    print(f"Collected {len(job_links)} new job links")

    for url in job_links:
        if len(job_data) >= max_jobs:
            break

        job_info = scrapeJobDetails(url)
        if job_info:
            job_data.append(job_info)
            print(f"Scraped job: {job_info['Title']} at {job_info['Company']}")

    if len(job_data) >= max_jobs:
        break

    driver.execute_script("window.scrollBy(0, 800);")
    time.sleep(2)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".base-search-card"))
        )
    except:
        break

if job_data:
    df = pd.DataFrame(job_data)
    df.to_csv("jobDescriptions.csv", index=False, lineterminator="\n")
    print("✅ Job descriptions saved to jobDescriptions.csv!")
else:
    print("No job data found!")

driver.quit()
