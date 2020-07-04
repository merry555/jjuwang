import os

os.system("pip3 install paramiko")

from tkinter import *
from tkinter import messagebox
import paramiko
import socket
import threading
import time
import smtplib
from email.mime.text import MIMEText
# wine64 python.exe Scripts/pip.exe install pyinstaller
# wine64 ~/.wine/drive_c/Python27/Scripts/pyinstaller.exe --onefile test.py
# https://popcorn16.tistory.com/38


# function ( save variable )
def run_cmd(sshClient, command):
    channel = sshClient.get_transport().open_session()
    channel.get_pty()
    channel.exec_command(command)
    out = channel.makefile().read()
    err = channel.makefile_stderr().read()
    returncode = channel.recv_exit_status()
    channel.close()
    return out, err, returncode

# email function
def email_function( send , email , fini):
    print("step1111")
    s = smtplib.SMTP('smtp.gmail.com',587)
    print("step2222")
    s.starttls()
    print("step3333")
    s.login('LEESU.management@gmail.com','ljh9521wn')
    print("step4444")
    print(send)

    if send == 1:
        msg = MIMEText('All job is finished')
        msg['Subject'] = 'All job is finished'

    elif send == 2:
        pass
    elif send == 3:
        #msg = MIMEText("%d is finished",%fini)
        msg = MIMEText(fini, 'html')
        msg['Subject'] = 'Something is finished'
    elif send == 4:
        pass
    else:
        pass
    s.sendmail("9521ljh@gmail.com", email ,msg.as_string())
    s.quit()
    # email_function( send )


def loop(localhostIP, psword, name, pid, email):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    pid_list = pid.split(' ')

    try:
        #ssh.connect(localhostIP, username=name, password=psword)
        client.connect(localhostIP, username=name, password=psword)
    except:
        messagebox.showinfo("Error", "Check Password or Hostname")
    else:
        for i in range(len(pid_list)): #이게 무슨의미지? 저 코드 -> pid_list길이 만큼 for문을 반복하는거얌!!
            out, err, returncode = run_cmd(client, "echo %s >> PID.txt"%pid_list[i])   
        #out, err, returncode = run_cmd(client, "echo %s >> PID.txt"%pid_list[i]) #이 코드까지만 포문 돌면댕 쨔 오호 하나더있어
        
        #make null file past_finished_PID.txt
        out, err, returncode = run_cmd(client, "if [ -f past_finished_PID.txt ]; then echo 'yes' ; else touch past_finished_PID.txt ; fi ")

        out, err, returncode = run_cmd(client, "cat PID.txt")#이코드부터
        print("step 1 =========================================================")
        out, err, returncode = run_cmd(client, "top -b -n 1 | grep {} | sed 's/^ *//g' | sed 's/ /\t/g' | cut -f1-2 > top.txt".format(name))
        out, err, returncode = run_cmd(client, 'grep -wFf PID.txt top.txt | cut -f1 > running_PID.txt')
        #out, err, returncode = ssh.exec_command('grep -wFf PID.txt top.txt | cut -f1 > YYY123.txt')
        out, err, returncode = run_cmd(client, 'grep -vFf running_PID.txt PID.txt > finished_PID.txt')
        out, err, returncode = run_cmd(client, " cat running_PID.txt | wc -l ")
        print("step 2 =========================================================")
        X1 = int(out.decode("utf-8").strip())
        print(X1)
        print("step 3 =========================================================")
        out, err, returncode = run_cmd(client, "diff past_finished_PID.txt finished_PID.txt | sed 's/> /row\t/g' | grep row | cut -f2 | wc -l")
        X2 = int(out.decode("utf-8").strip())
        print(X2)
        print("step 4 =========================================================")
        #here finish 근데 for문 실행이 어디까지 되어야하는거얌?? 왜냐면 파이썬 에서는 이렇게 들여쓰기를 잘 해줘야돼가지구!!
        #All job is finished = 1
        #running = 2
        #Some job is finished
        #Nothing is finished
        command = 'if [ %s == 0 ]; then echo "All_job_is_finished" ; else if [ %s != 0 ] ; then echo "Some_job_is_finished"; else echo "Nothing_is_finished"; fi; fi'%(X1,X2)
        stdin, stdout, stderr = client.exec_command(command)
        result = stdout.readline().rstrip()
        print(result)

        out, err, returncode = run_cmd(client, "cat finished_PID.txt")
        fini = out.decode("utf-8").strip()
        print(fini)
        #echo - All job is finished , running, Some job is finished, Nothing is finished
        if result == "All_job_is_finished" :
            send = 1
            print("Y111")
            email_function(send, email, fini)
            print("Y222")
            out, err, returncode = run_cmd(client, "rm past_finished_PID.txt running_PID.txt PID.txt finished_PID.txt top.txt")
            #여기에  함수 종료시켜야댕 근데 뭘해도안되는거같오 잠만!!! 내가 함 해볼겡!!
            return 0

        elif result == "Some_job_is_finished":
            send = 3
            email_function(send , email, fini )

        elif result == "Nothing_is_finished":
            send = 4 
            #email_function(send)

        else:
            print(result)

        # move file
        out, err, returncode = run_cmd(client, "mv finished_PID.txt past_finished_PID.txt")
        # remove file
        out, err, returncode = run_cmd(client, "rm running_PID.txt PID.txt finished_PID.txt top.txt")
        
        


# UI
def address_check():
    #localhostIP = socket.gethostbyname(socket.gethostname())
    localhostIP = E0.get()
    psword = E2.get()
    name = E1.get()
    pid = E3.get()
    email = E4.get()

    # loop(localhostIP, psword, name, pid, email)

    exit_code = loop(localhostIP, psword, name, pid, email)

    if exit_code is 0:
        print("finish !!!!!")
        sys.exit(1)

    threading.Timer(60, address_check).start()

    print("thread")


# main menu
top = Tk()
top.title("jjuwang")
top.config(bg="white")

L1 = Label(top, text = "Host")
L1.place(x = 10,y = 10)
E1 = Entry(top, bd = 5)
E1.pack()
E1.place(x = 60,y = 10)

L2 = Label(top,text = "Pass")
L2.place(x = 10,y = 60)
E2 = Entry(top,bd = 5)
E2.pack()
E2.place(x = 60,y = 60)

L3 = Label(top,text = "PID")
L3.place(x = 10,y = 110)
E3 = Entry(top,bd = 5)
E3.pack()
E3.place(x = 60,y = 110)

L4 = Label(top,text = "Email")
L4.place(x = 10,y = 160)
E4 = Entry(top,bd = 5)
E4.pack()
E4.place(x = 60,y = 160)

L0 = Label(top,text = "IP")
L0.place(x = 10,y = 250)
E0 = Entry(top,bd = 5)
E0.pack()
E0.place(x = 60,y = 250)

B = Button(top, text = "Submit", command=address_check)
B.place(x = 100, y = 300)
top.geometry("500x500")
top.mainloop()


'''
host : ubuntu
pass : 1234
ip : 13.125.169.154

'''