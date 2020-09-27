import sys
import socket
from os import _exit as quit
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes, hmac

from cryptography.hazmat.primitives import padding as pad
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def load_keys():
    with open("private_key.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
    )
    with open("public_key.pem", "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
    )
    return public_key,private_key

def check_signature(key,msg,signature):
    h = hmac.HMAC(key, hashes.SHA256())
    h.update(msg)
    h.verify(signature)


def main():
    # parse arguments
    public_key,private_key  = load_keys()


    if len(sys.argv) != 3:
        print("usage: python3 %s <port>" % sys.argv[0])
        quit(1)
    port = sys.argv[1]
    #type of encryption
    type_encryption = sys.argv[2]
    
    # open a socket
    listenfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listenfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # bind socket to ip and port
    listenfd.bind(('', int(port)))

    # listen to socket
    listenfd.listen(1)

    # accept connection
    (connfd, addr) = listenfd.accept()


    #getting the key and iv and decrypting it
    key_enc = connfd.recv(1024)
    iv_enc = connfd.recv(1024)
    aes_key = private_key.decrypt(
        key_enc,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
            )
        )
    aes_iv = private_key.decrypt(
        iv_enc,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
            )
        )

    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(aes_iv))
    decryptor = cipher.decryptor()


    #unpadder = pad.PKCS7(16).unpadder()

    # message loop
    while(True):
        msg_ct = connfd.recv(1024)
        signature = connfd.recv(1024)
        check_signature(aes_key,msg_ct,signature)
        
        print("Received: ", msg_ct.decode(), signature)

        #msg = (decryptor.update(msg_ct) + decryptor.finalize())
        #data = unpadder.update(msg) + unpadder.finalize()
        #print("Received from client: %s" % msg.decode().strip())

#        # You don't need to send a response for this assignment
#        # but if you wanted to you'd do something like this
#        msg = input("Enter message for client: ")
#        connfd.send(msg.encode())

    # close connection
    connfd.close()
    listenfd.close()

if __name__ == "__main__":
    main()