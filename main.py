from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dataclasses import dataclass
import seleniumwire.undetected_chromedriver.v2 as uc
from seleniumwire.utils import decode
import selenium
import time
import requests
import csv
import json

CUSTOM_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
SEC_CH_UA = '"Google Chrome";v="112", " Not;A Brand";v="99", "Chromium";v="112"'

def request_interceptor(request):
    # Delete previous UA
    del request.headers['user-agent']
    # Set a new custom UA
    request.headers["user-agent"] = CUSTOM_UA
    # Delete previous Sec-CH-UA
    del request.headers["sec-ch-ua"]
    # set Sec-CH-UA
    request.headers["sec-ch-ua"] = SEC_CH_UA

    # Blocks image assets
    if request.path.endswith((".png",".jpg",".gif")):
        request.abort()

def get_json(body,headers):
    body=decode(body,headers.get(
                'Content-Encoding','identity'
            ))
    decoded=body.decode("utf-8")
    json_object=json.loads(decoded)
    return json_object 


def write_output(account_infos):
    with open("output.csv","w",newline='') as csvfile:
        info_writer= csv.writer(csvfile, delimiter=',')
        for i in account_infos:
            info_writer.writerow([i.profile_link,i.name,i.neighborhood,i.neighbours,i.posts_this_week])
    

@dataclass
class AccountInfo:
    profile_link:str
    name:str
    neighborhood:str 
    neighbours:str
    posts_this_week:str

chrome_options=uc.ChromeOptions()
chrome_options.add_argument('--ignore-certificate-errors')
driver=uc.Chrome(
    driver_executable_path="chromedriver.exe",
    options=chrome_options,
    seleniumwire_options={
        "request_interceptor":request_interceptor
    },use_subprocess=True)

driver.request_interceptor = request_interceptor



def main_account():
    credentials = []
    with open("credentials.txt","r") as f:
        for i in f.readlines():
           credentials.append(i) 
    return credentials

credentials = main_account()
email = credentials[0]
password = credentials[1]

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

def get_profiles():
    profiles=[]
    with open("profiles.txt","r") as f:
        for i in f.readlines():
            if i != "\n":
                profiles.append(i)
        return profiles
    
def account_view(account_url):
    time.sleep(2)
    driver.get(account_url)
    time.sleep(3)

def get_profile_details(json_body):
    location = json_body.get('data', {}).get('user', {}).get('userProfileState', {}).get('location', {}) 
    display_name = json_body.get('data', {}).get('user', {}).get('name', {}).get('displayName', '')
    neighborhood = location.get("neighborhood", {})
    favorites_url_path = neighborhood.get("neighborhoodFavoritesUrlPath", "")
    neighborhood_name = neighborhood.get("shortName", "")
    city = neighborhood.get("city", "")
    state = neighborhood.get("state", "")

    return display_name,neighborhood_name,favorites_url_path,city,state



def neighbour_view(neighborhood_url):
    time.sleep(2) 
    driver.get(f"https://nextdoor.com{neighborhood_url.split('favorites')[0]}?is=neighbour_profile")
    time.sleep(3)

def write_failed_accounts(failed_accounts):
    with open("failed_accounts.txt","w") as f:
        f.writelines(failed_accounts)

def get_neighbourhood_details(neighborhood_url):
    driver.get(f"https://nextdoor.com{neighborhood_url.split('favorites')[0]}?is=neighbour_profile")
    results = []
    time.sleep(5)
    try:
        neighbourhood_profile_stat=driver.find_element(By.CLASS_NAME,"neighborhoodProfileStats")
        children=neighbourhood_profile_stat.find_elements(By.XPATH,"*")
        for child in children:
            el = child.find_element(By.CSS_SELECTOR,".blocks-eftpa8 > span")
            results.append(el.text)
    except selenium.common.exceptions.NoSuchElementException as error:
        print("ERROR OCCURED WHILE GETTING DETAILS OF THIS ACCOUNT",driver.current_url)
        print("PLEASE REMOVE IT AND RUN AGAIN")
        results = []
    
    return results


def main():
    login(email,password)
    #wait = WebDriverWait(driver,100)
    #element = wait.until(EC.title_contains("News Feed"))
    time.sleep(20)
    account_infos = []
    failed_accounts = []
    profiles = get_profiles()
    profile_counter = 0
    for i in profiles:
        profile_counter+=1
        account_view(i)
        print("scrapping account : ",i)
        if profile_counter < 20:

            for request in driver.requests:
                if request.url.endswith("profileTopCard?"):
                    json_body=get_json(body=request.response.body,headers=request.response.headers)
                    display_name,short_name,neighbourhood_url,city,state = get_profile_details(json_body)
                    if neighbourhood_url: 
                        results = get_neighbourhood_details(neighborhood_url=neighbourhood_url) 
                        if len(results) > 1:
                            account_infos.append(AccountInfo(profile_link=i,name=display_name,neighborhood=f"{short_name} {city},{state}",neighbours=results[0],posts_this_week=results[1]))   
                            break
                        else:
                            account_infos.append(AccountInfo(profile_link=i,name="NULL",neighborhood="NULL",neighbours="NULL",posts_this_week="NULL"))   
                            print("error occured for this account ",i)
                            failed_accounts.append(i)
                            break
            time.sleep(3)
            del driver.requests
        else:
            print("completed 20 accounts")

            # change the sleep value to your desired value (in seconds)
            pause_time = 60
            print("scrapper paused for ",pause_time)
            time.sleep(pause_time)
            profile_counter = 0
            continue

    
    driver.quit()
    write_failed_accounts(failed_accounts)
    write_output(account_infos)
    print("output.csv has been generated")
        


    

        
            

 



        



if __name__ == "__main__":
    main()
    
    
