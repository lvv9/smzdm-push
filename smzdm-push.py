import requests
from bs4 import BeautifulSoup
import re
import time

import pymysql

import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
from email.header import Header

# user-agent needed by smzdm
headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0"
        }

# network connection
session = requests.Session()
session.headers.update(headers)

# database connection
conn = pymysql.connect(host='127.0.0.1', user='root', passwd='passwd', db='mysql', charset='utf8')
cur = conn.cursor()
cur.execute("use scraping")

# email configuration
smtpHost = "host"
sslPort = "465" # default port so not being used
iMail = "email" # as "from" and "to" address
password = "password"

encoding = 'utf-8'

while True:

    if int(time.strftime("%M", time.localtime())) % 5 == 0: 
    # to see whether the minute hand is pointing to some multiple of 5, therefore scrapes every 5 minutes

        r = session.get("http://search.smzdm.com/?c=home&s=路由器&order=time")
        # the page it scrapes, use server built-in search in case the web updates too frequently that it don't catch up therefore reduce requests

        soup = BeautifulSoup(r.text)
        tags = soup.find_all("h5") # article tags

        for tag in tags:
            cur.execute("select * from pages where url = %s", (tag.a["href"]))
            if cur.rowcount == 0: # means the database didn't store this url
                url = tag.a["href"]
                cur.execute("insert into pages (url) values (%s)", (url))
                conn.commit()
                title = tag.a["title"]
                if re.search('(华硕|asus)', title.lower()): # some rules on title to see if the product meets our needs, if yes sends email
                    mail = MIMEText(url.encode(encoding), 'plain', encoding)
                    mail['Subject'] = Header(title, encoding)
                    mail['From'] = iMail
                    mail['To'] = iMail
                    mail['Date'] = formatdate()
                    smtp = smtplib.SMTP_SSL(smtpHost)
                    smtp.login(iMail, password)
                    smtp.sendmail(iMail, iMail, mail.as_string())
                    smtp.quit()

    time.sleep(55)
