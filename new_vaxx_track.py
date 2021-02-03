import os
import time 
import hashlib 
from urllib.request import urlopen, Request 
import urllib
import csv, smtplib, ssl
import smtplib
import yagmail
from datetime import datetime
import openpyxl
import ezsheets
from bs4 import BeautifulSoup


keywords = ["now open", "schedule now", "now available", \
    "vaccines available", "appointments available", "register now", \
         "registration now open", "appointments now open", "book now", "now booking", "now providing", "health"]

email_addresses = []
phone_numbers = []
email_contents = []
alpha = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
alpha_upper = [x.upper() for x in alpha]


def build_email(dashboard, changed_urls, date_time):
    # Send email
    for i in range(0, len(changed_urls)):
        j = 0
        while(dashboard['A' + str(j+2)] != ""):
            if changed_urls[i] == dashboard['C' + str(j+2)]:
                email_contents.append('There has been a change in the ' + \
                    dashboard['A' + str(j+2)] + \
                    ' vaccine website in ' + dashboard['B' + str(j+2)] + '. This change was detected at ' + date_time + '.')
                email_contents.append(" \n ")
            j+=1
        i+=1
    send_email(email_contents, date_time)

def send_email(email_contents, date_time):
    ss3 = ezsheets.Spreadsheet('1kQJnM2-1c18cb0r3cY18adcU5-mQohrk7ar8Bf7llAA')
    user_info = ss3[0]
    i = 0
    while(user_info['A' + str(i+2)] != ""):
        email_addresses.append(user_info['A' + str(i+2)])
        i+=1
    email_contents.append(" \n ")
    yag = yagmail.SMTP('EMAIL@gmail.com', 'PASSWORD')
    email_contents.append('Check the dashboard for links and more information: https://tinyurl.com/vaxxtracknj')
    yag.send(email_addresses, date_time + ' Vaccine Website Update', email_contents)

def send_SMS(dashboard, url):
    # Send email
    i = 0
    while(dashboard['A' + str(i+2)] != ""):
        if url == dashboard['C' + str(i+2)]:
            yag = yagmail.SMTP('EMAIL@gmail.com', 'PASSWORD')
            text = 'There has been a change in the ' + dashboard['A' + str(i+2)] + \
                 ' vaccine website. Check the dashboard for more information: https://tinyurl.com/vaxxtracknj'
            yag.send(phone_numbers, "", text)
        i+=1

def update_spreadsheet(dashboard, url, new_hash, date_time):
    i = 0
    while(dashboard['A' + str(i+2)] != ""):
        if(dashboard['C' + str(i+2)] == url):
            dashboard['D' + str(i+2)] = new_hash
            dashboard['E' + str(i+2)] = date_time
        i+=1

def get_urls(dashboard):
    urls = []
    i = 0
    while(dashboard['A' + str(i+2)] != ""):
        urls.append(dashboard['C' + str(i+2)])
        i+=1
    return urls

def parse_keywords(url, name, keywords_sheet):
    change_detected = 0
    raw_html = urllib.request.urlopen(url).read().lower()
    soup = BeautifulSoup(raw_html, features='lxml')
    col = ""
    new_keywords = []
    for i in range(0, len(keywords)):
        if keywords[i] in soup.get_text():
            new_keywords.append(keywords[i])
    # Match the company (find col)
    i = 1
    while(keywords_sheet[alpha_upper[i] + '1'] != ""):
        if(keywords_sheet[alpha_upper[i] + '1'] == name):
            # Match found
            col = alpha_upper[i]
        i+=1
    # Check the current status of the keywords. If it was N before, and now it is Y, send change.
    k = 0
    while(keywords_sheet[col + str(k+2)] != ""):
        if(keywords_sheet[col + str(k+2)] == "Y" and (keywords_sheet['A' + str(k+2)] not in new_keywords)):
            #print("changing")
            keywords_sheet[col + str(k+2)] = "N"
        if(keywords_sheet[col + str(k+2)] == "N") and (keywords_sheet['A' + str(k+2)] in new_keywords): # BIG DEAL
            print("changing, big deal " + keywords_sheet[col + '1'])
            keywords_sheet[col + str(k+2)] = "Y"
            change_detected = 1   
        k+=1
    return change_detected            

    for i in range(0, len(keywords)):
        if(soup.find_all(keywords[i]) != ""):
            # Match name
            i = 0
            stop_point = 0
            while(keywords_sheet[alpha_upper[i]+ str(1)] != ""):
                print(keywords_sheet[alpha_upper[i] + str(1)])
                if(keywords_sheet[alpha_upper[i] + str(1)] == name):
                    print("match")
                    print(keywords_sheet[alpha_upper[i] + str(1)])
                    stop_point = i
                    break
                break
            i+=1
            
    return 0

def check_websites(dashboard, urls, keywords_sheet):
    change_detected = 0
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    changed_urls = []
    for i in range(1, len(urls)+1):
        # Get the old website info
        old_hash = dashboard['D' + str(i+1)]
        # Check new hash
        url = Request(urls[i-1], headers={'User-Agent': 'Mozilla/5.0'})
        response = urlopen(url).read()
        new_hash = hashlib.sha224(response).hexdigest()
        # check if new hash is same as the previous hash, nothing changed
        if(old_hash == new_hash):
            #print("no change")
            continue
        # if something changed in the hashes, send an alert
        elif(dashboard['D' + str(i+1)] == ""): #empty
            #print("nothing there")
            update_spreadsheet(dashboard, urls[i-1], new_hash, date_time)

        elif(old_hash != new_hash): # Outdated or empty
            #print("insignicant change")
            if(parse_keywords(urls[i-1], dashboard['A' + str(i+1)], keywords_sheet) == 1): # change detected
                #print("sig change")
                changed_urls.append(urls[i-1])
                change_detected = 1
                update_spreadsheet(dashboard, urls[i-1], new_hash, date_time)
            continue
    if(change_detected == 1):
        build_email(dashboard, changed_urls, date_time)
        send_SMS(dashboard, changed_urls)

def main():
    # Dashboard
    ss = ezsheets.Spreadsheet("SS")
    dashboard = ss[0]

    # User Information
    ss2 = ezsheets.Spreadsheet('SS')
    user_info = ss2[0] # first sheet

    # Keyword checker
    ss3 = ezsheets.Spreadsheet('SS')
    keywords_sheet = ss3[0]

    # Get URLS
    urls = get_urls(dashboard)

    #3get_old_emails(user_info)

    #welcome_email(email_addresses)
    #welcome_text(phone_numbers)
    #send_email()

    # Check the website and if neccesary, update the spreadsheet
    check_websites(dashboard, urls, keywords_sheet)


main()
