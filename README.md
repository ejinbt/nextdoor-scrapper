# Nextdoor scrapper




## Installation


```bash
  git clone https://github.com/ejinbt/nextdoor-scrapper
  cd nextdoor-scrapper
  pip install -r requirements.txt
```

    
## Run Locally
+ Put profile links in profiles.txt file
+ you need to type your account email and password , then only bot can access the nextdoor website to scrape (you can use the one you given to me)
+ type your email and password in credentials.txt file
+ first line should contain email and second line should contain password
+ then run the code below
```bash
  python main.py
```
+ when the program is done  , a output.csv file will be generated (it will not be generated after each profile)

## Some things to note while using this scrapper
+ scrapper is made to be little slow to overcome nextdoor from restrict our bot
+ wait until scrapper logins to the main account , before letting it run itself. in case of any erros , rerun the program (sometimes it ask for email verification code , but it can be bypassed if you rerun)
+ after login successful , scrapper is made to be ignore errors if it failed to scrape some account and continue scraping other accounts, so you can let the scraper do its work (accounts that failed to scrape will be shown in cmd and NULL value will be set for those accounts in csv file)
+ also list of failed accounts will be outputed in failed_accounts.txt file . so you can rerun scrapper with just those accounts (make sure to copy it contents to profiles.txt)
+ if profiles.txt contains links that are not profile , program will fail
+ nextdoor has tight protection against scrapper , so it might restrict the bot if you scrape in bulk in small period of time ( go to main function and read the commented line)
+ scrapper will be paused for 1 min after 20 accounts , you can change the sleep time in code



## Support

For support, contact us on fiverr

