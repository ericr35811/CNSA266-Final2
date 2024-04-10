import socket, struct


HOST = '127.0.0.1'
EOT = '<EOT>'

class MySocket:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def waitForConn(self, host, port):
        self.sock.bind((host, port))
        self.sock.listen(5)
        conn, addr = self.sock.accept()

    def connectTo(self, host, port):
        self.sock.connect((host, port))

    def sendData(self, string):
        data = struct.pack('>I', len(string)) + bytes(string)
        sent = 0
        while sent < len(data):
            sent += self.sock.send(data)

    def receiveData(self):


if __name__ == '__main__':
    s = MySocket('127.0.0.1', 9000)
    print str(s.sendData("joe mama"))







class ServerSockets:
    def __init__(self, numOfSockets, portBase):
        self.host = HOST
        self.sockets = {}

        for i in range(portBase, portBase + numOfSockets):
            print(i)

        print(self.sockets)

# if __name__ == '__main__':
#     s = ServerSockets(4, 9090)