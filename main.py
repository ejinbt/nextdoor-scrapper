from selenium import webdriver
from selenium.webdriver.chrome.service import Service 
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from dataclasses import dataclass
import time
import csv
import click

@dataclass
class AccountInfo:
    name:str
    neighbourhood:str
    neighbours:str
    posts_this_week:str
chrome_options=Options()
email = str(input("Please type your account email : "))
password = str(input("Password: "))

## comment the below line to see the automation running on browser 
chrome_options.add_argument("--headless=new")
driver = webdriver.Chrome(service=webdriver.chrome.service.Service(executable_path="chromedriver.exe"),options=chrome_options)
driver.maximize_window()
def get_profiles():
    profiles = []
    with open("profiles.txt","r") as f:
        for i in f.readlines():
            print(i)
            profiles.append(i)
    return profiles

def write_output(account_infos):
    with open("output.csv","w+",newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        for i in account_infos:
            spamwriter.writerow([i.name,i.neighbourhood,i.neighbours,i.posts_this_week])

def login(email,password):
    driver.get("https://nextdoor.com/login/?ucl=1")
    driver.implicitly_wait(10)    
    email_element = driver.find_element(By.CLASS_NAME,"blocks-kddr16")
    email_element.clear()
    email_element.click()
    email_element.send_keys(email)
    driver.implicitly_wait(10)
    password_element = driver.find_element(By.CLASS_NAME,"blocks-fpd3nj")
    password_element.clear()
    password_element.click()
    password_element.send_keys(password)
    driver.implicitly_wait(10)
    submit_element = driver.find_element(By.CLASS_NAME,"blocks-19al32i")
    submit_element.send_keys(Keys.ENTER)
    driver.implicitly_wait(10)
   

def profile(profile_url):
    driver.switch_to.new_window('tab')
    time.sleep(5)
    driver.get(profile_url)
    time.sleep(3)
    profile_name = driver.find_element(By.CSS_SELECTOR,".blocks-1lk4gab > h2").text
    time.sleep(5)
    address_element=driver.find_element(By.CLASS_NAME,"blocks-16m6fnr")
    ActionChains(driver).move_to_element(address_element).click().perform()
    driver.implicitly_wait(10)
    return profile_name

def get_neighbourhood_details():
    results = []
    neighbourhood = driver.find_element(By.CLASS_NAME,"blocks-11jkfwa").text
    results.append(neighbourhood) 
    neighbourhood_profile_stats = driver.find_element(By.CLASS_NAME,"neighborhoodProfileStats")
    children = neighbourhood_profile_stats.find_elements(By.XPATH,"*")
    for child in children:
        el = child.find_element(By.CSS_SELECTOR,".blocks-eftpa8 > span")
        results.append(el.text) 
    return results

def main():
    account_infos = []
    print("Welcome !!")

    login(email,password)
    time.sleep(10)
    profiles = get_profiles()
    for url in profiles:
        profile_name = profile(profile_url=url)
        time.sleep(5)
        results = get_neighbourhood_details()
        account_infos.append(AccountInfo(name=profile_name,neighbourhood=results[0],neighbours=results[1],posts_this_week=results[2])) 
        time.sleep(2) 
    driver.quit()
    write_output(account_infos)


if __name__ == "__main__":
        main()