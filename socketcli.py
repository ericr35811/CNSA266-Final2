import socket

HOST = '127.0.0.1'
PORT = 9002

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((HOST, PORT))

#    d = str(raw_input('> '))

s.send(bytes("asdf"))

data = s.recv(1024)
if data:
    print(data)
else:
    print('C: no data')

while True:
    pass
#
# s.send()
# data = s.recv(1024)
# if data:
#     print(data)
# else:
#     print('C: no data')