#!/usr/bin/env python3

import socket
import threading
import sys
import os
from server import Server

MYPORT = 1234
HOST = ''

print(f"Starting Controller.py on {MYPORT}")
# Af = send information via IPv4 || STREAM = TCP connection
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
all_connections = []

# bind socket to address and port
sock.bind((HOST, MYPORT))

print(f"listening on port {MYPORT}")
# number of connection want to allow
sock.listen(1)

while True:
    clientsocket, client_addr = sock.accept()
    print(f"Connection from {client_addr} has been established")
    all_connections.append(clientsocket)
    clientsocket.send(bytes("Connection OK", "utf-8"))

    s = Server(str(client_addr[0]))

    '''
    Implementation to do:
    - not all msg_recv is utf-8. Look/fix at client.py's PUT
    '''

    while True:

        msg_recv = clientsocket.recv(1024).decode("utf-8")
        msg_split = msg_recv.split("\n")
        protocol = msg_split[0].upper()
        response = ""

        try:

            if protocol == "PUT":
                print("received message PUT")
                filename = msg_split[1]
                if msg_split[2] == "DATA_START" and msg_split[4] == "DATA_FIN":
                    data = msg_split[3]
                else:
                    raise RuntimeError("the data is missing!")

                s.write(filename=filename, data=data)
                response = "OK PUT"

            elif protocol == "WRITE":
                print("received message WRITE")
                filename = msg_split[1]
                if msg_split[2] == "DATA_START" and msg_split[4] == "DATA_FIN":
                    data = msg_split[3]
                else:
                    raise RuntimeError("the data is missing!")

                s.write(filename=filename, data=data)
                response = "OK WRITE"

            elif protocol == "LS":
                print("received message LS")
                response = s.ls()

            elif protocol == "CHDIR":
                print("received message CHDIR")
                new_dir = msg_split[1]
                s.chdir(new_dir)
                response = "OK CHDIR"

            elif protocol == "GET":
                print("received message GET")
                findfile = msg_split[1]
                response = s.get(findfile)

            elif protocol == "FIND":
                print("received message FIND")
                findfile = msg_split[1]
                response = s.find(findfile)

            elif protocol == "BYE" or protocol == "QUIT":
                print("received message BYE")
                print("Disconnecting...")
                clientsocket.close()
                break

            elif protocol == "CWD":
                response = s.cwd()

            elif protocol == "MKDIR":
                new_dir = msg_split[1]
                response = "OK MKDIR: " + s.mkdir(new_dir)

        except Exception as e:
            response = str(e)


        clientsocket.send(bytes(response, "utf-8"))
        

################

#!/usr/bin/env python3

import socket
import threading
import sys
import os

#Goal: remote server FTP

class Server:

    """Act as a data store where each method mimics command line arguments

    Attributes:
        homepath (str): path in OS where all clients' files should be stored in

    Constructor parameters:
        client (str): unique string to store that user's files

    """

    # TODO: make private for production use
    # TODO: write in path to use
    homepath = "/usr/src/server"

    # constructor
    def __init__(self, client):
        self.createhomedir()
        self.client = client
        self.curr_dir = self.homepath
        self.usr_path = os.path.join(self.homepath, self.client)
        self.mkdir(self.client)
        self.chdir("/")


    def createhomedir(self):
        if os.path.isdir(self.homepath):
            os.chdir(self.homepath)
        else:
            os.mkdir(self.homepath)

    # Void: writes given data to the given name of file in current directory
    def write(self, filename, data):
        file_path = os.path.join(self.curr_dir, filename)
        file = open(file_path, "wb")
        file.write(data)
        file.close()

    # String: makes new directory in the current directory.
    def mkdir(self, new_dir):
        new_path = os.path.join(self.curr_dir, new_dir)
        if not os.path.isdir(new_path):
            os.mkdir(new_path)

        return str(new_path)

    # void: change cwd to the specified directory
    def chdir(self, gotodir):

        if gotodir == "/":
            os.chdir(self.usr_path)
            self.curr_dir = self.usr_path
        else:

            try:
                new = os.path.join(self.usr_path, gotodir)
                os.chdir(new)
                self.curr_dir = new
            except OSError:
                raise RuntimeError("!" + str(new) + " does not exist")

    # String: returns all files and directories in cwd
    def ls(self):
        allfiles = []
        alldir = []
        for x in os.listdir(self.curr_dir):
            if x.split()[0] != "." and os.path.isdir(os.path.join(self.curr_dir, x)):
                alldir.append(x)
            else:
                if x.split()[0] != "." and os.path.isfile(os.path.join(self.curr_dir, x)):

                    allfiles.append(x)

        response = "Directories:\n %s\n  Files:\n %s\n" % (alldir, allfiles)
        return response

    # String: returns first instance of file in cwd
    def get(self, findfile):
        for root, dirs, files in os.walk(self.curr_dir):
            if findfile in files:
                file = os.path.join(self.curr_dir, findfile)

        f = open(file, "r")
        response = "File: " + file + " found\nDATA\n" + f.read() + "\n.\n"
        return response

    # String: returns first instance of file in user path
    def find(self, findfile):

        for root, dirs, files in os.walk(self.usr_path):
            if findfile in files:
                # TODO: make path lead to file
                file = os.path.join(root, findfile)
                break

        f = open(file, "r")
        response = "File: " + file + " found\nDATA\n" + f.read() + "\n.\n"
        return response

    # String: returns current working directory
    def cwd(self):
        if os.getcwd() == self.curr_dir:
            return str(self.curr_dir)
        else:
            raise RuntimeError("OS cwd does not match expected")





