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

