# Before start usingthe program you should setup it for yourself. Find all comments which contain Attention word in the file
# and do the needfull steps which are described in the marked comments.
# Please do not use mailboxes, to send notiffication messages from, with two stage authentification.
# If you struggle any difficulties to setup the program for yourself, feel free to apply kozirev8@gmail.com
# If any other question, feel free to let me know, I'll do my best to help.


import threading
import ipaddress
import sys
import time
import os
import smtplib 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def main():
    while(True):
        circle()

def key_press(e):
    a=input()
    e.clear()
    
    

def circle():
    e=threading.Event()
    e.set()
    '''This is main function of the program'''
    StartProgram=True # checks if the problem can be started without errors
    ListToMonitor=initial_dialog() #as a result we get list of ips to use in monitoring
    if(ListToMonitor==None): # check if the list exists, if there is no list we get error message
        print("File IpAdressList contains zero IPs, or is corrupted, or does not exist.\n\nThe program will be closed soon.")
        StartProgram=False
        time.sleep(7)
    elif(len(ListToMonitor)==0):
        print("File IpAdressList contains zero IPs, or is corrupted, or does not exist.\n\nThe program will be closed soon.")
        StartProgram=False
        time.sleep(7)
    if  StartProgram:
        print(f"The following list is monitored: {ListToMonitor}")
        time.sleep(3)
        print("\n\nMonitoring has started! \n\n")
    while(StartProgram):
        c=[]
        for i in ListToMonitor:
            c.append(threading.Thread(target=IP_Op.do_infinite_ping, args=(e,i,3,))) #create independent thread for each ip address
            # i is ip address from list, 3 is a delay between pings
        c.append(threading.Thread(target=key_press,args=(e,)))
        for i in c:
            i.start()
        for i in c:
            i.join() # since fuction iside thread is infinite, join will never happen
        print("It is the end!")
        time.sleep(15)
        StartProgram=False


def initial_dialog():
    '''This fuction is used to make initial setup'''
    print("******** The program is used for remote IPs ping monitoring ********")
    print("******** The program is designed only for Windows OS **********\n")
    print("Do you want to do any initial setup? If yes print yes, otherwise print no.\n")
    bool1=True #bool1 is boolean which check if we need to do initial setup
    while(bool1):
        a=str(input())
        if(a.lower()=="yes"):
            bool2=True #bool2 is boolean which check if we need to add ip
            while(bool2):
                b=IP_Op.ask_ip() # b is tuple which contains ip,boolean
                IP_Op.add_ip_tofile(address=b,file="IpAdressList") # adds ip address to file
                if(b[1]==True): # if user want more ip then
                    bool2=IP_Op.do_you_need_more_ip() # ask if user really want more ip
                else:
                    bool2=False
                n=IP_Op.what_ip_ismonitored(file="IpAdressList") #returns list of ip and boolean which indicates whether the list really exists
                if(n[1]==False):
                    bool1=False # if the list is empty or corrupted  we will breal error and read error message                  
            bool3=True # checks if we want to remove any ip
            while(bool3 and bool1): # bool1 is used here since we do not want the operation if lis (file) empty or  corrupted
                removeMore=IP_Op.remove_ip_address(file="IpAdressList",adressList=n[0]) 
                # adressList is a list which was read from file to delete ip from
                if(removeMore):
                    bool3=IP_Op.do_you_need_remove_more_ip()
                else:
                    bool3=False
            bool1=False # now initial setup is needed
        elif(a.lower()=="no"):
            print("You chose no, no initial setup will be made.\n")
            IP_Op.what_ip_ismonitored(file="IpAdressList")  
            bool1=False
        else:
            print("Incorrect input, you should press only yes or now. Try again please\n")
    resultList=IP_Op.read_ip_from_file(file="IpAdressList")
    if(resultList!=None): #if the list in not empty and exists (is checked in IP_Op.read_ip_from_file)
        resultList=set(IP_Op.read_ip_from_file(file="IpAdressList"))
        IP_Op.remove_duplicated_ip_from_file(file="IpAdressList", resultList=resultList)
    time.sleep(1) 
    return resultList # as a result we get list of IPs to work with   

def good_time(localtime,mode):
    ''' The function is created to give well readable time format. The function has two parameters,
    localtime is an instance of structure of time.localtime() structure. Mode could be 0 or 1 or 2. If 0 method returns string
    Date: {2}.{1}.{0} Time UTC+3 {3}:{4}:{5} where 0 is day, 1 is month, 2 is a year and 3,4,5 is hour,
    minute and second relatively. If  mode=1 is chosen it retruns string {2}_{1}_{0}_timeUTC3_{3} where 0 is day,
    1 is month and 2 is year and 3 is hour. If mode=2 is chosen string date{2}_{1}_{0} is returned where 0 is day, 1 is month,
    2 is year'''
    if(mode==0):
        d=[localtime.tm_mday,localtime.tm_mon, localtime.tm_year, localtime.tm_hour, localtime.tm_min, localtime.tm_sec]
        p=d
        for i in range(0,len(d)):
            if int(p[i])<10:
                p[i]="0"+str(p[i])
        d=p               
        return "Date: {2}.{1}.{0} Time UTC+3 {3}:{4}:{5}".format(*d) # *d means that we unpack list as individual values
    if(mode==1):
        d=[localtime.tm_mday,localtime.tm_mon, localtime.tm_year, localtime.tm_hour]
        p=d
        for i in range(0,len(d)):
            if int(p[i])<10:
                p[i]="0"+str(p[i])
        return "date{2}_{1}_{0}_timeUTC3_{3}".format(*d)
    if(mode==2):
        d=[localtime.tm_mday,localtime.tm_mon, localtime.tm_year]
        p=d
        for i in range(0,len(d)):
            if int(p[i])<10:
                p[i]="0"+str(p[i])
        return "date{2}_{1}_{0}".format(*d)
    
    
class MyMailActivity:
    def send_negative_mail(ipAddress,email_sender,email_receiver):
        '''The method sends negative mail if one ip is not reachable'''
        ipAddress=str(ipAddress)
        time1str=good_time(localtime=time.localtime(),mode=0)
        # Attention! write your own mail subject, do not delete words inside brackets time1str
        subject=f"MTT Oy error notification {time1str}"
        msg = MIMEMultipart() 
        msg['From'] = email_sender
        msg['To'] = ", ".join(email_receiver)
        msg['Subject']= subject
        # Attention! write your own mail message, do not delete words inside brackets ipAddress and time1str
        body=f"Dear Partner,\n\nWe observe that address {ipAddress} is not reachable within last 30 seconds. Now {time1str}.\n\nWe ask you to investigate the issue and undertake all necessary steps to solve the problem.\n\nBest Regards,\nMTT Oy Network Monitor Robot"

        msg.attach(MIMEText(body, 'plain'))
        text = msg.as_string()  

        connection = smtplib.SMTP('smtp.gmail.com', 587) # Attention! This should be settings of you smtp server
        connection.starttls()  
        connection.login(email_sender, '1111111') # Attention! Put password of your mailbox to send mails about alarms from
        connection.sendmail(email_sender, email_receiver, text)
        connection.quit()

            
    def send_positive_mail(ipAddress,email_sender,email_receiver):
        '''The method sends positive mail if ip is reachable again'''
        ipAddress=str(ipAddress)
        time1str=good_time(localtime=time.localtime(),mode=0)
        # Attention! write your own mail subject, do not delete words inside brackets time1str
        subject=f"MTT Oy recovery notification {time1str}"
        msg = MIMEMultipart() 
        msg['From'] = email_sender
        msg['To'] = ", ".join(email_receiver)
        msg['Subject']= subject
        # Attention! write your own message, do not delete words inside brackets ipAddress and time1str
        body=f"Dear Partner,\n\nWe observe that address {ipAddress} has recovered and is stable within last 60 seconds. Now {time1str}.\n\nWe ask you to investigate and provide us RFO.\n\nBest Regards,\nMTT Oy Network Monitor Robot"

        msg.attach(MIMEText(body, 'plain'))
        text = msg.as_string()  

        connection = smtplib.SMTP('smtp.gmail.com', 587) # Attention! This should be settings of you smtp server
        connection.starttls()  
        connection.login(email_sender, '111111') # Attention! Put password of your mailbox to send mails about alarms from
        connection.sendmail(email_sender, email_receiver, text)
        connection.quit()

class IP_Op:
    
    def ask_ip():
        '''The fuction is used to ask user to  provide Ip address for the program.
        Returns tuple ip and boolean if we want to add it to the list of ip in further'''
        check1=True
        while(check1):
            print("What ip address would you like to choose for monitoring? \n\nIf you do not want to add any ip address:\nPress any button and follow to next recommendations.\n")
            a=str(input())
            try:
                address1=ipaddress.IPv4Address(address=str(a))
            except  ipaddress.AddressValueError:
                #print(sys.exc_info()) #it is very useful command
                print("You entered incorrect ip address please try to enter ip address again. \n\n")
                print("If you do not want to enter ip address print no.\nIf you still want to add any other ip address, press any other key.")
                word=input()
                if str(word).upper()=="NO":
                    check1=False 
                    toadd=False # we do not want to add any ip
                    address1=None # we retrun empty value instead of ip
                time.sleep(2)
            else:
                check1=False
                toadd=True
        q=(address1,toadd)
        return q
    
    def remove_duplicated_ip_from_file(file, resultList):
        '''The function is used to remove duplicated ip addressess from IpAdressList'''
        try:
            with open(file+".txt","w") as f:
                for i in resultList:
                    f.write(i+"\n")
        except FileNotFoundError:
            print("The file IpAdressList.txt is not reachable or corrupted.\nTry to delete IpAdressList.txt if it exists and do initial setup process.\nThe program will be closed soon.\n")


    def add_ip_tofile(file, address):
        '''The function is used to add IP to the desired file'''
        if(address[1]):
            file=str(file)
            file_name=file+".txt"
            with open(file_name, mode="a") as f:
                f.write(f"{address[0]}\n")
            

    def what_ip_ismonitored(file):
        '''The funtcion shows what IPs are monitored in file, The fuction returns tuple which composed of
        List of ip and booilean value which prevents the program internal error if the file is empty or corrupted'''
        ToContinue=True # is used to detect internal error if file is corrupted or does not exist
        try:
            with open(file+".txt",mode="r") as f:
                b=[]
                for i in f:
                    b.append(i.strip())
                f.seek(0)
        except FileNotFoundError:
            print("The file IpAdressList.txt is not reachable or corrupted.\nTry to delete IpAdressList.txt if it exists and do initial setup process.\nThe program will be closed soon.\n")
            ToContinue=False
            time.sleep(3)
            b=[]
            return (b,ToContinue)
        else:
            print("Do not worry if you see duplicated IPs,\nthey will be removed before monitoring start.\nThe following List of ip adresses will be monitored:")
            for i in b:
                print(i)
            print("\n")
            return (b,ToContinue)
        
    def do_you_need_more_ip():
        '''Just asks whether the user want more IPs to monitor. Return True or False value'''
        print("Do yo want to add more IP? Print yes or no.\n")
        a=""
        while(str(a).lower()!="yes" or str(a).lower()!="no" ):
            a=input()
            if str(a).lower()=="yes":
                return True
            elif str(a).lower()=="no":
                return False
            else:
                print("You should print only yes or no\n")
                
    def do_you_need_remove_more_ip():
        '''Just asks whether the user want remove more IPs from monitoring'''
        print("Do yo want to remove more IP? Print yes or no.\n")
        a=""
        while(str(a).lower()!="yes" or str(a).lower()!="no" ):
            a=input()
            if str(a).lower()=="yes":
                return True
            elif str(a).lower()=="no":
                return False
            else:
                print("You should print only yes or no\n")
                
    def remove_ip_address(file,adressList): #addressList is the list of ip which is read from file, we gonna removing ip from the list
        '''The function is used to remove Ip addressess from file'''
        print("Do you want to remove any ip addresses? Print only yes or no.")
        a=""
        bool1=True
        while(bool1==True):
            a=input()
            if str(a).lower()=="yes":
                print("You chose yes, please see below list of IP which can be removed.")
                IP_Op.what_ip_ismonitored(file)
                print("Choose ip to remove and print it:")
                text=""
                bool2=True # checks if the provided address is in the ip list
                removeMoreIP=True
                while(bool2):
                    text=str(input())
                    if(str(text) in adressList):             
                        adressList.remove(str(text))
                        with open(f"{file}.txt",mode="w") as f:
                            for i in adressList:
                                f.write(f"{i}\n")
                        bool1=False
                        bool2=False
                        removeMoreIP=True
                    else:
                        print("The ip address should be in the list. Please try again.\n")
                        print("If you do not want to remove any IP print yes. If other is printed, it is considered as no.\n")
                        test=str(input())
                        if test.lower()=="yes":    
                            bool1=False
                            bool2=False
                            removeMoreIP=False
                        else:
                            print("You chose no then try again please.\n")
                            removeMoreIP=True
                        
            elif str(a).lower()=="no":
                print("You chose no, no ip adressess will be removed.\n")
                bool1=False
                removeMoreIP=False
            else:
                print("You should print only yes or no.\n")
                removeMoreIP=True
            return removeMoreIP
                     
    def read_ip_from_file(file):
        '''The function is used to read Ip addresses from file and return it as list'''
        try:
            with open(file+".txt",mode="r") as f:
                b=[]
                for i in f:
                    b.append(i.strip())
                f.seek(0)
        except FileNotFoundError:
            print("The file IpAdressList.txt is not reachable or corrupted.\nTry to delete IpAdressList.txt if it exists and do initial setup process.\nThe program will be closed soon.\n")
        else:
            return b # list of ip addresses
        
    def do_ping(b,t100):
        '''The function do 1 ping of the remote IP (b) within t100 interval, and retruns 1,0 tuple if attempt was good,
        otherwise we recive tuple 0,1'''
        
        a=os.system(f"ping -n 1 {b}") # Attention! you can try to change the command if you do not use OS Windows
        
        h=good_time(time.localtime(),1)
        h2=good_time(time.localtime(),2)
        
        current_directory = os.getcwd() #reads current directory
        upperFolderName=str(b)
        folder1name=str(b)+h2
        folder1=os.path.join(current_directory, upperFolderName, folder1name) # build name of folder to prit files into
        if not os.path.exists(folder1): # if the path do not exist then 
            os.makedirs(folder1) # create it now!
                
        with open(os.path.join(folder1,f"ping_{h}_{b}.txt"),mode="a") as f:
            t=good_time(time.localtime(),0)
            if(a==int(0)):
                f.write(f"The remote destination {b} is reachable, everyting is OKAY. {t} \n")
                time.sleep(int(t100))
                return (1,0)
            elif(a==int(1)):
                f.write(f"Ping {b} failed! {t} \n")
                time.sleep(int(t100))
                return(0,1)
        
    
    def do_infinite_ping(e,b,t100):
        '''Do infinite ping of the remote IP every t100 seconds'''
        negativeMailSent=False
        positiveCounter=0 #is used to send positive or negative mail
        negativeCounter=0 #is used to send positive or negative mail
        positivePingAttempts=0 # total counter, became 0 every hour
        negativePingAttempts=0 # total counter, became 0 every hour
        while(e.is_set()):
            p1=IP_Op.do_ping(b,t100) # we recive tuple as a results of the function 1,0 if successful, 0,1 if failes
            positivePingAttempts=positivePingAttempts+p1[0]
            negativePingAttempts=negativePingAttempts+p1[1]
            t=time.localtime()
            # block below writes percent of positive and negative attempt every hour
            if t.tm_min==59 and t.tm_sec>50 and (positivePingAttempts>10 or negativePingAttempts>10):
                # we need positivePingAttempts>10 or negativePingAttempts>10 to prevent event to take place several times
                h=good_time(time.localtime(),1)
                h2=good_time(time.localtime(),2)
                current_directory = os.getcwd()
                upperFolderName=str(b)
                folder1name=str(b)+h2
                folder1=os.path.join(current_directory, upperFolderName, folder1name)
                with open(os.path.join(folder1,f"ping_{h}_{b}.txt"),mode="a") as f:
                    k=100*positivePingAttempts/(positivePingAttempts+negativePingAttempts)
                    f.write(f"{b}__positivePingAttempts_Number_is__{positivePingAttempts}\n")
                    f.write(f"{b}__negativePingAttempts_Number_is__{negativePingAttempts}\n")
                    f.write(f"{b}__Percent of_positivePingAttempts__is__{k}\n")
                    f.write("\n")
                    positivePingAttempts=0
                    negativePingAttempts=0 
            incPositiveCounter=positiveCounter+p1[0]
            incNegativeCounter=negativeCounter+p1[1]
            if incPositiveCounter>positiveCounter:
                negativeCounter=0
                positiveCounter=incPositiveCounter
            elif incNegativeCounter>negativeCounter:
                negativeCounter=incNegativeCounter
                positiveCounter=0
            if negativeCounter==3 and negativeMailSent==False:
                print("Negative mail was sent")
                # Attention! Put your own mail settings in the code below, do not remove f"{b}":
                MyMailActivity.send_negative_mail(f"{b}","111111@gmail.com",["22222@gmail.com","222322@gmail.com","44444@22222@gmail.com"])
                negativeMailSent=True
            if positiveCounter==20 and negativeMailSent==True:
                print("Positive mail was sent")
                # Attention!Put your own mail settings in the code below, do not remove f"{b}":
                MyMailActivity.send_positive_mail(f"{b}","111111@gmail.com",["22222@gmail.com","222322@gmail.com","44444@22222@gmail.com"])
                negativeMailSent=False

if __name__ == '__main__':
    main()


