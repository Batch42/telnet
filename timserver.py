import socket
import sys
from threading import Thread
from collections import defaultdict as dd

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('',10023))

conns=dd()#conn to username dict
users = dd()#username to password dict
bklog = dd()#username to inbox

#this function services each user session
def talk(conn):
    conn.sendall('Connection recieved.\r\n'.encode())
    #com = conn.recv(128).decode('unicode_escape')#eats unicode nonsense at start of telnet.
    while True:
        try:
            global conns
            global users
            global bklog
            com = conn.recv(128).decode('unicode_escape').strip()#blocks thread, gets string from client
            m= com.split(' ')
            if len(m)==0:
                continue
            if len(m)==1:
                m.append('default')
            if len(m)==2:
                m.append('default')
            name = conns[conn]#name of user logged in through AUTH, is None b4hand
            m[0]=m[0].upper()
            if m[0] == 'CRTE':
                if conns[conn] is None and len(users)>0:
                    conn.sendall(('206 Not connected as a user.\r\n').encode())
                    continue
                if m[1] in users:
                    conn.sendall(("203 User " + m[1] + " already exists.\r\n").encode())
                users[m[1]]= m[2]
                bklog[m[1]]=[]
                if len(users)==1:
                    conn.sendall(("105 User " + m[1]+ " created as superuser.\r\n").encode())
                else:
                    conn.sendall(("104 User "+ m[1]+" created.\r\n").encode())
            elif m[0] == 'AUTH':
                if conns[conn] is not None:
                    conn.sendall(("202 Already connected as " + conns[conn] +".\r\n").encode())
                    continue
                if m[1] not in users:
                    conn.sendall(("204 Invalid user name or password.\r\n").encode())
                    continue
                if users[m[1]]==m[2]: #if password is correct
                    if m[1] in conns.values():
                        conn.sendall(('201 User ' +m[1]+' already connected.\r\n').encode())
                    else:
                        conn.sendall(('102 Connected as ' +m[1]+'.\r\n').encode())
                        conns[conn]=m[1]
                        for l in bklog[m[1]]:
                            conn.sendall(l)
                        bklog[m[1]].clear()
                else:
                    conn.sendall(("204 Invalid user name or password.\r\n").encode())
            elif m[0]=='SEND':
                if conns[conn] is None:
                    conn.sendall(('206 Not connected as a user.\r\n').encode())
                    continue
                if m[1] not in users:
                    conn.sendall(('200 User ' + m[1] + " doesn't exist\r\n").encode())
                    continue
                message = '100 Message from ' + conns[conn] + ' follows: "' + com[6+len(m[1]):]+'"\r\n'
                for k in conns:
                    if conns[k]==m[1]:
                        k.sendall(message.encode())
                        continue
                bklog[m[1]].append(message.encode())
                conn.sendall('101 Message sent.\r\n'.encode())
            elif m[0]=='QUIT':
                conn.sendall('103 Bye.\r\n'.encode())
                conns[conn]=None
                conn.close()
                break
            else:
                conn.sendall(('205 No such command "'+str(m[0])+'".\r\n').encode())
        except Exception as ex:
            if str(ex) == '[Errno 32] Broken pipe':
                conns[conn]=None
                conn.close()
                break
            print(ex)

print('TIM sever online.')
s.listen(3)

# this loop recieves new connections and starts a session thread for each
while True:
    try:
        #wait to accept a connection - blocks thread
        conn, addr = s.accept()
        conns[conn]=None
        print(str(addr) + ' connected.')
        t=Thread(target=talk, args=[conn])
        t.start()
    except:
        s.close()
        sys.exit()
