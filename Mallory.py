import sys
import socket
from os import _exit as quit

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


def load_key():
    with open("public_key.pem", "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
    )
    return public_key

def main():

    public_key  = load_key()
    # parse arguments
    if len(sys.argv) != 5:
        print("usage: python3 %s <port>" % sys.argv[0])
        quit(1)

    host  = sys.argv[1]
    #From alice    
    in_port = sys.argv[2]
    #To bob
    out_port  = sys.argv[3]
    #type of encryption
    type_encryption = sys.argv[4]

    #Listening from alice
    listenfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listenfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listenfd.bind(('', int(in_port)))
    listenfd.listen(1)
    (connfd, addr) = listenfd.accept()



    #This is for sending to bob
    clientfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientfd.connect((host, int(out_port)))



    # message loop
    while(True):
        #Receiving
        msg = connfd.recv(1024).decode()
        print("Received from client Alice: %s" % msg)

        #Relaying the message to Bob
        clientfd.send(msg.encode())




    clientfd.close()
    connfd.close()
    listenfd.close()

if __name__ == "__main__":
    main()