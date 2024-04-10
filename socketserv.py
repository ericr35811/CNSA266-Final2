import socket
from time import sleep
from socketcli import Test

class ServerSocket:
    def __init__(self, portbase):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)




    def fssdga(self):
        return 'asdfh'

HOST = '127.0.0.1'
PORT = 9002

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(5)

conn, addr = s.accept()
print 'Connected by', addr

while True:
    data = conn.recv(1000)

    if data:
        print data
        conn.send(data)

        assert isinstance(data, Test)
        print data.a, data.b
    else:
        print "no data"
        break
        # conn.send("S: no data")



