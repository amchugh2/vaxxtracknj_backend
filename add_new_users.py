from datetime import datetime, date
import ezsheets
import yagmail

def welcome_email(email):
    yag = yagmail.SMTP('vaccineupdatechecker@gmail.com', '7ch3urn5')
    welcome = []
    welcome.append('Thank you for signing up for VaxxTrackNJ! This service is in BETA TESTING and new changes are being rolled out on a consistent basis. For now:')
    welcome.append('')
    welcome.append('Please visit our website https://amchugh2.github.io/vaxxtracknj/ for information on our Community Dashboard and usage disclaimer.')
    welcome.append('')
    welcome.append('We appreciate your support!')
    welcome.append('- VaxxTrackNJ')
    yag.send(email, 'Welcome to VaxxTrackNJ!', welcome)

def welcome_text(cell):
    yag = yagmail.SMTP('vaccineupdatechecker@gmail.com', '7ch3urn5')
    text = 'Welcome to VaxxTrackNJl! You are now signed up for alerts. Visit our website for more info: https://amchugh2.github.io/vaxxtracknj/'
    yag.send(cell, "", text)

def add_email(user_info, email):
    #print("adding")
    i = 0
    while(user_info['A' + str(i+2)] != ""):
        i+=1
    user_info['A' + str(i+2)] = email
    user_info['C' + str(i +2)] = "Welcome email sent"
    welcome_email(email)

def add_cell(user_info, cell, service):
    #print("adding")
    i = 0
    while(user_info['B' + str(i+2)] != ""):
        i +=1
    if service == "Verizon":
        cell += "@vtext.com"
        user_info['B' + str(i+2)] = cell
    if service == "AT&T":
        cell += "@txt.att.net"
        user_info['B' + str(i+2)] = cell
    if service  == "T-Mobile":
        cell += "@tmomail.net"
        user_info['B' + str(i+2)] = cell
    if service == "Boost Mobile":
        cell += "@myboostmobile.com"
        user_info['B' + str(i+2)] = cell
    if service == "Cricket":
        cell += "@sms.mycricket.com"
        user_info['B' + str(i+2)] = cell
    if service == "Metro PCS":
        cell += "@mymetropcs.com"
        user_info['B' + str(i+2)] = cell
    if service == "Tracfone":
        cell += "@mymetropcs.com"
        user_info['B' + str(i+2)] = cell
    if service == "U.S. Cellular":
        cell += "@email.uscc.net"
        user_info['B' + str(i+2)] = cell
    if service == "Virgin Mobile":
        cell += "@vmobl.com"
        user_info['B' + str(i+2)] = cell
    user_info['D' + str(i +2)] = "Welcome text sent"
    welcome_text(cell)

def add_new_users(dashboard, user_info):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    today = date.today()
    curr_date = today.strftime("%m/%e/%Y")
    # Annoying format of dates
    if(curr_date[0] == "0"):
        curr_date = curr_date[1:]
    curr_date = curr_date.replace(" ", "")
    curr_hour = int(current_time[:2])
    curr_min = int(current_time[3:5])
    print(curr_min)
    i = 0
    while(dashboard['A' + str(i+2)] != ""): # iterate
        signup_date = dashboard['A' + str(i+2)][0:9].strip()
        signup_min = int(dashboard['A' + str(i+2)][-5:-3])
        signup_hour = int(dashboard['A' + str(i+2)][-8:-6])
        if((signup_date == curr_date) and (signup_hour == curr_hour) and (signup_min == (curr_min - 1))):
            ''''
            print("sending to " + dashboard['B' + str(i+2)])
            print("sending to " + dashboard['D' + str(i+2)])
            print("")
            '''
            if(dashboard['D' + str(i+2)] != ""):
                email = dashboard['D' + str(i+2)]
                add_email(user_info, email)
            if(dashboard['B' + str(i+2)] != ""):
                cell = dashboard['B' + str(i+2)]
                cell = ''.join(i for i in cell if i.isdigit())
                service = dashboard['C' + str(i+2)]
                add_cell(user_info, cell, service)
        i+=1

def main():
    # User Information
    ss2 = ezsheets.Spreadsheet('1Kbqh0S5Ohnm1JycrDVSYLhq7379eLLHvq5tl7WXp8Vo')
    dashboard = ss2[0] # first sheet

    # Formatted User List
    ss3 = ezsheets.Spreadsheet('1kQJnM2-1c18cb0r3cY18adcU5-mQohrk7ar8Bf7llAA')
    user_info = ss3[0]


    add_new_users(dashboard, user_info)


main()