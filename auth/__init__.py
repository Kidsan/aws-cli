import sys
import os
class User:
    def __init__(self, username, password, access_key, secret):
        self.username = username
        self.password = password
        self.access_key = access_key
        self.secret = secret

class Auth:
    def __init__(self):
        try:
            credentials_file = open("passwd.txt", "r")
        except:
            print("Could not read the passwd.txt file, please make sure it is located in", os.getcwd())
            sys.exit("No passwd file")
        self.credentials = []
        for line in credentials_file:
            values = line.split("\t") # create a list for each line in the passwd.txt
            if(len(values) < 4):
                sys.exit("passwd.txt file is invalid")
            # strip newline / whitespace character at the end
            self.credentials.append(User(values[0],values[1],values[2], values[3].rstrip()))
        
    def authenticate(self, username, password):
        if username == "":
            sys.exit("No username given")
        # lambda function filters the list of credentials in the passwd file to find lines where the username and password
        # match the passed arguments. We expect to only get either 1 or 0 entries in the resultant list.
        filter_clients = filter(lambda credential: credential.username == username and credential.password == password , self.credentials)
        clients = list(filter_clients)
        if len(clients) == 0:
            return False
        if len(clients) != 1:
            sys.exit("passwd.txt file is invalid - may contain duplicates")
        else:
            return clients[0]
