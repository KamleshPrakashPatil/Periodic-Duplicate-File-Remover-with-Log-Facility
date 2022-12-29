from sys import *
import os
import hashlib
import schedule
import time
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def hashfile(path,blocksize = 1024):
    fd = open(path,'rb')
    hasher = hashlib.md5()
    buf = fd.read(blocksize)

    while len(buf)>0:
        hasher.update(buf)
        buf = fd.read(blocksize)

    fd.close()

    return hasher.hexdigest()    

def FindDuplicates(path):
    flag = os.path.isabs(path)
    iCnt = 0

    if flag == False:
        path = os.path.abspath(path)

    exists = os.path.isdir(path)

    duplicates = {}

    if exists:
        for foldername,subfoldername,filenames in os.walk(path):
            for file in filenames:
                path = os.path.join(foldername,file) 
                iCnt+=1

                file_hash = hashfile(path)

                if file_hash in duplicates:
                    duplicates[file_hash].append(path)

                else:
                    duplicates[file_hash] = [path]    

        return duplicates,iCnt           
    else:
        print("Invalide Path")

def WriteDuplicate(dict1,Count,Stime):

    results = list(filter(lambda x: len(x) > 1,dict1.values()))

    listDups = list()
    D_Cnt = 0

    if not os.path.exists("Duplicate_Records"):
        try:
            os.mkdir("Duplicate_Records")
        except:
            pass

    separator = "-"*80
    
    log_path = os.path.join("Duplicate_Records","%s.txt"%time.ctime())

    f = open(log_path,'w')

    f.write(separator+"\n")
    f.write("Duplicate Deleted File Record : %s\n"%time.ctime())            
    f.write(separator+"\n")
    f.write("Starting Time of Scanning : %s\n"%str(Stime))
    f.write("Total Number of Files Scanned : %s\n"%str(Count))

    if len(results) >0: 

        iCnt = 0

        for result in results:
            iCnt = 0
            for subresult in result:
                iCnt+=1
                if iCnt>=2:
                    listDups.append("\n"+subresult)
                    os.remove(subresult) 
                    D_Cnt+=1
        f.write("Total Number of duplicate files found : %s\n"%str(D_Cnt))
        for Dups in listDups:
            f.write(Dups) 
    else:
        f.write("No Duplicate Files Found........\n")

    f.write(separator+"\n")
    f.close()  

    return log_path 

def Send_mail(files,send_to):
    files=os.path.abspath(files)
    
    from_addr = "rajputkamlesh1889@gmail.com"
    to_addr = send_to
    content = time.ctime()

    msg = MIMEMultipart()
    msg['From'] = "Kamlesh's Laptop"
    msg['To'] = to_addr
    msg['Subject'] = "Periodic Duplicate File Remover Record"
    body = MIMEText(content,'plain')
    msg.attach(body)

    filename = files

    with open(filename,'r') as f:
        attachment = MIMEApplication(f.read(),Name = basename(filename))
        attachment['Content-Disposition'] = 'attachment; filename="{}"'.format(basename(filename))

    msg.attach(attachment)    

    smtp = smtplib.SMTP(host = 'smtp.gmail.com',port = 587)
    smtp.starttls()

    smtp.login("rajputkamlesh1889@gmail.com", "lmhxlwceno")

    smtp.send_message(msg,from_addr=from_addr, to_addrs = to_addr)
    
    smtp.quit()

def Task():
        start = time.ctime()
        Result,Count = FindDuplicates(argv[1])
        File = WriteDuplicate(Result,Count,start)

        Send_mail(File,argv[3])

def main():

    if(len(argv)<5):
        print("Please Refer Readme file before using the script")
        exit()

    else:
        Itime = int(argv[2])
        schedule.every(Itime).minutes.do(Task)

        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    main()    
