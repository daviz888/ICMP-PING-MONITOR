import threading
import ipaddress
import sys
import time
import os
import smtplib 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#Several bugs wer solved in this program version.

# To use the program you should do some changes in mail adresses. Please find comments in code to do it


def main():
    StartProgram=True
    ListToMonitor=initial_dialog()
    if(ListToMonitor==None):
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
            c.append(threading.Thread(target=IP_Op.do_infinite_ping, args=(i,3)))                    
        for i in c:
            i.start()
        for i in c:
            i.join()


def initial_dialog():
    print("******** The program is used for remote IPs ping monitoring ********")
    print("******** The program is designed only for Windows OS **********\n")
    print("Do you want to do any initial setup? If yes print yes, otherwise print no.\n")
    bool1=True
    while(bool1):
        a=str(input())
        if(a.lower()=="yes"):
            bool2=True
            while(bool2):
                b=IP_Op.ask_ip()
                IP_Op.add_ip_tofile(address=b,file="IpAdressList")
                if(b[1]==True):
                    bool2=IP_Op.do_you_need_more_ip()
                else:
                    bool2=False
                n=IP_Op.what_ip_ismonitored(file="IpAdressList")
                if(n[1]==False):
                    bool1=False                   
            bool3=True
            while(bool3 and bool1):
                removeMore=IP_Op.remove_ip_address(file="IpAdressList",adressList=n[0]) 
                if(removeMore):
                    bool3=IP_Op.do_you_need_remove_more_ip()
                else:
                    bool3=False
            bool1=False
        elif(a.lower()=="no"):
            print("You chose no, no initial setup will be made.\n")
            IP_Op.what_ip_ismonitored(file="IpAdressList")  
            bool1=False
        else:
            print("Incorrect input, you should press only yes or now. Try again please\n")
    resultList=IP_Op.read_ip_from_file(file="IpAdressList")
    time.sleep(1) 
    return resultList   

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
        return "Date: {2}.{1}.{0} Time UTC+3 {3}:{4}:{5}".format(*d)
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
        ipAddress=str(ipAddress)
        time1str=good_time(localtime=time.localtime(),mode=0)
        
        #Print your own subject:
        subject=f"Your error notification {time1str}"
        msg = MIMEMultipart() 
        msg['From'] = email_sender
        msg['To'] = ", ".join(email_receiver)
        msg['Subject']= subject
        body=f"Dear Partner,\n\nWe observe that address {ipAddress} is not reachable within last 30 seconds. Now {time1str}.\nt"

        msg.attach(MIMEText(body, 'plain'))
        text = msg.as_string()  
        
        # Put you email server settings  
        connection = smtplib.SMTP('smtp.gmail.com', 587) 
        connection.starttls()
        
        #Put your e-mail server password below:
        connection.login(email_sender, 'YourPassword')
        connection.sendmail(email_sender, email_receiver, text)
        connection.quit()

            
    def send_positive_mail(ipAddress,email_sender,email_receiver):
        ipAddress=str(ipAddress)
        time1str=good_time(localtime=time.localtime(),mode=0)
        subject=f"MTT Oy recovery notification {time1str}"
        msg = MIMEMultipart() 
        msg['From'] = email_sender
        msg['To'] = ", ".join(email_receiver)
        msg['Subject']= subject
        body=f"Dear Partner,\n\nWe observe that address {ipAddress} has recovered and is stable within last 60 seconds. Now {time1str}.\n"

        msg.attach(MIMEText(body, 'plain'))
        text = msg.as_string()  

        connection = smtplib.SMTP('smtp.gmail.com', 587) 
        connection.starttls()  
        connection.login(email_sender, 'Samara12345')
        connection.sendmail(email_sender, email_receiver, text)
        connection.quit()

class IP_Op:
    
    def ask_ip():
        '''The fuction is used to ask user to  provide Ip address for the program'''
        check1=True
        while(check1):
            print("What ip address would you like to choose for monitoring? \n\nIf you do not want to add any ip address:\nPress any button and follow to next recommendations.\n")
            a=str(input())
            try:
                address1=ipaddress.IPv4Address(address=str(a))
            except  ipaddress.AddressValueError:
                #print(sys.exc_info()) - good command to use in your code 
                print("You entered incorrect ip address please try to enter ip address again. \n\n")
                print("If you do not want to enter ip address print no.\nIf you still want to add any other ip address, press any other key.")
                word=input()
                if str(word).upper()=="NO":
                    check1=False
                    toadd=False
                    address1=None
                time.sleep(2)
            else:
                check1=False
                toadd=True
        q=(address1,toadd)
        return q

    def add_ip_tofile(file, address):
        '''The function is used to add IP to the desired file'''
        if(address[1]):
            file=str(file)
            file_name=file+".txt"
            with open(file_name, mode="a") as f:
                f.write(f"{address[0]}\n")
            

    def what_ip_ismonitored(file):
        '''The funtcion shows what IPs are monitored in file and retruns list of ip addressess which is monitored'''
        ToContinue=True
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
            print("The following List of ip adresses will be monitored:")
            for i in b:
                print(i)
            print("\n")
            return (b,ToContinue)
        
    def do_you_need_more_ip():
        '''Just asks whether the user want more IPs to monitor'''
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
                
    def remove_ip_address(file,adressList):
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
                bool2=True
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
        '''The function is used to read Ip addresses from file and return it is list'''
        try:
            with open(file+".txt",mode="r") as f:
                b=[]
                for i in f:
                    b.append(i.strip())
                f.seek(0)
        except FileNotFoundError:
            print("The file IpAdressList.txt is not reachable or corrupted.\nTry to delete IpAdressList.txt if it exists and do initial setup process.\nThe program will be closed soon.\n")
        else:
            return b
        
    def do_ping(b,t100):
        '''The function do 1 ping of the remote IP (b) within t100 interval'''
        
        a=os.system(f"ping -n 1 {b}")
        
        h=good_time(time.localtime(),1)
        h2=good_time(time.localtime(),2)
        
        current_directory = os.getcwd()
        folder1name=str(b)+h2
        folder1=os.path.join(current_directory, folder1name)
        if not os.path.exists(folder1):
            os.makedirs(folder1)
                
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
        
    
    def do_infinite_ping(b,t100):
        '''Do infinite ping of the remote IP every t100 seconds'''
        negativeMailSent=False
        positiveCounter=0 
        negativeCounter=0 
        positivePingAttempts=0
        negativePingAttempts=0
        while(True):
            p1=IP_Op.do_ping(b,t100)
            positivePingAttempts=positivePingAttempts+p1[0]
            negativePingAttempts=negativePingAttempts+p1[1]
            t=time.localtime()
            if t.tm_min==59 and t.tm_sec>50 and (positivePingAttempts>10 or negativePingAttempts>10):
                h=good_time(time.localtime(),1)
                h2=good_time(time.localtime(),2)
                current_directory = os.getcwd()
                folder1name=str(b)+h2
                folder1=os.path.join(current_directory, folder1name)
                with open(os.path.join(folder1,f"ping_{h}_{b}.txt"),mode="a") as f:
                    k=100*positivePingAttempts/(positivePingAttempts+negativePingAttempts)
                    f.write(f"{b}__positivePingAttempts_Number_is__{positivePingAttempts}\n")
                    f.write(f"{b}__negativePingAttempts_Number_is__{negativePingAttempts}\n")
                    f.write(f"{b}__Percent of_positivePingAttempts__is__{k}\n")
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
            if negativeCounter==4 and negativeMailSent==False:
                print("Negative mail was sent")
                # Put below emails information 
                MyMailActivity.send_negative_mail(f"{b}","Youremailsentfrom@gmail.com",["Yourmailsendto1@gmail.com","Yourmailsendto2@gmail.com"])
                negativeMailSent=True
            if positiveCounter==20 and negativeMailSent==True:
                print("Positive mail was sent")
                # Put below emails information 
                MyMailActivity.send_positive_mail(f"{b}","Youremailsentfrom@gmail.com",["Yourmailsendto1@gmail.com","Yourmailsendto2@gmail.com"])
                negativeMailSent=False

if __name__ == '__main__':
    main()


