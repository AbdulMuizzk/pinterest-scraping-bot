from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from loguru import logger
import pandas as pd
import time
import os

scrape_Data = {}

def scroll_down(scrolls, driver):
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
        except Exception as e:
            logger.exception(e)
            pass
        
def search_by_filter(driver,filter_query):
        try:
            time.sleep(2)
            search_bar = driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div[1]/div[2]/div/div/div[2]/div/div/div/div[4]/div/div/div[2]/input")
            search_bar.send_keys(filter_query)
            search_bar.send_keys(Keys.ENTER)
            time.sleep(5)
        except Exception as e:
            logger.info("An error occured")

def log_in(driver,email,password):
    try:
        driver.get("https://www.pinterest.com/")
        time.sleep(1)
        login_button = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/div/div/div/div/div/div/div[1]/div/div/div[1]/div/div[2]/div[2]/button")
        login_button.click()
        time.sleep(2)
        email_input = driver.find_element(By.XPATH,"/html/body/div[1]/div/div[1]/div/div[2]/div/div/div/div/div/div[4]/form/div[2]/fieldset/span/div/input")
        email_input.send_keys(email)
        time.sleep(2)
        pass_input = driver.find_element(By.XPATH,'/html/body/div[1]/div/div[1]/div/div[2]/div/div/div/div/div/div[4]/form/div[4]/fieldset/span/div/input')
        pass_input.send_keys(password)
        log_btn_2 = driver.find_element(By.XPATH,'/html/body/div[1]/div/div[1]/div/div[2]/div/div/div/div/div/div[4]/form/div[7]/button')
        log_btn_2.click()
        time.sleep(1)
    except Exception as e:
        logger.error(e)

def get_images_link(driver,max_scrolls):
        scrolls = 0
        links_list = []
        count = 0
        title_xpath = "/html/body/div[1]/div[1]/div[2]/div/div/div/div/div[2]/div/div/div/div/div[2]/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div/div[2]/div/div/div/div/div/a/h1"
        image_xpath = "/html/body/div[1]/div[1]/div[2]/div/div/div/div/div[2]/div/div/div/div/div[2]/div/div/div/div/div/div/div/div/div/div[1]/div/div/div[1]/div/div[1]/div/div/img"
        profile_xpath = "/html/body/div[1]/div[1]/div[2]/div/div/div/div/div[2]/div/div/div/div/div[2]/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div/div[3]/div[2]/div/div/div/div[1]/div/div[2]/div[1]/a"
        web_xpath = "/html/body/div[1]/div[1]/div[2]/div/div/div/div/div[2]/div/div/div/div/div[2]/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div/div[1]/div[1]/div/div/div/div/div/a"

        while scrolls < max_scrolls:   
            for pin_link in driver.find_elements(By.TAG_NAME,'a'):
                try:
                    class2 = pin_link.get_attribute("class")
                    if class2 == "Wk9 xQ4 CCY S9z DUt iyn kVc agv LIa":
                        link = pin_link.get_attribute("href")
                        if link not in links_list:
                            links_list.append(link)              
                except NoSuchElementException or StaleElementReferenceException:
                    # print("No pink link found or is stale")
                    continue
            scrolls = scrolls+1
            print(f'You are performing the {scrolls} scroll')
            scroll_down(scrolls,driver)
            time.sleep(2)
        for link in links_list:
            title = ""
            image_high_res = ""
            profile_url = ""
            web_url = ""
            try:
                driver.get(link)
                time.sleep(2)
                try:
                    title = driver.find_element(By.XPATH,title_xpath)
                    title = title.get_attribute("innerText")
                except NoSuchElementException:
                    # print("No title was found")
                    pass
                try:
                    image_high_res = driver.find_element(By.XPATH,image_xpath)
                    image_high_res = image_high_res.get_attribute("src")
                except NoSuchElementException:
                    # print("No high res image found")
                    pass
                try:
                    profile_url = driver.find_element(By.XPATH,profile_xpath)
                    profile_url = profile_url.get_attribute("href")
                except NoSuchElementException:
                    # print("No profile url was found")
                    pass
                try:
                    web_url = driver.find_element(By.XPATH,web_xpath)
                    web_url = web_url.get_attribute("href")
                except NoSuchElementException:
                    # print("No web url was found")
                    pass

                scrape_Data[count] = {
                            "pin_url":link,
                            "title":title,
                            "image_url": image_high_res,
                            "web_url":web_url,
                            "profile_url": profile_url
                }
                print(scrape_Data[count])
                count = count+1
                 
                # print(f"Succesfully saving the {count} item in dict")
            except StaleElementReferenceException or NoSuchElementException:
                # print("page not found and title not retreived")
                pass
        return scrape_Data


def change_dict_to_df(data_scraped, search_query,combination):
    df = pd.DataFrame(data_scraped)
    df = df.T
    actual_columns = {
        "pin_url": "Pin Link",
        "title":  "Pin Name",
        "image_url": "Image URL",
        "web_url": "Website Link",
        "profile_url":"User URL"
    } 
    df = df.loc[:,df.columns.isin(combination)]            
    column_names = list(df.columns.values)
    for col in column_names:
        if col in actual_columns.keys():
            df.rename(columns={col:actual_columns[col]},inplace=True)

    if os.path.exists(os.path.join(os.path.dirname(__file__)+'/scraped_data.xlsx')):
        path_to_file = os.path.join(os.path.dirname(__file__)+'/scraped_data.xlsx')
        os.remove(path_to_file)
        name = "scraped_data_" + search_query + ".xlsx"
        df.to_excel(name,index=False)
    else:
        name = "scraped_data_" + search_query + ".xlsx"
        df.to_excel(name,index=False)

def main(email,password,search_query,combination,max_scrolls):
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    log_in(driver,email,password)
    search_by_filter(driver,search_query)
    scrape_Data = get_images_link(driver,max_scrolls)
    change_dict_to_df(scrape_Data, search_query,combination)
    driver.quit()


if __name__ == "__main__":
    f = open("inputs.txt")
    s = f.readlines()
    s = [x.strip() for x in s]

    
    email = s[0]
    password = s[1]
    max_scrolls = s[2]
    combination = s[3].split(" ")
    search_query = s[4:]
    print(search_query)
    for i in search_query:
        main(email,password,i,combination,int(max_scrolls))
