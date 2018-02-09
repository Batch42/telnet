import socket
from threading import Thread
from collections import defaultdict as dd

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind(('',23))
conns=dd

def talk(conn):
    global conns
    while conns[conn]:
        m = conn.recv(64).decode()



#Start listening on socket
s.listen(3)

#now keep talking with the client
while True:
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
    conns[conn]=True
    t=Thread(target=talk, args=[conn])
    t.start()
