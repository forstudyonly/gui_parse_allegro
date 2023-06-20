import os
from core.interface import start_interface

with open("access_token.txt", "r", encoding="utf-8") as file:
    access_token = file.read()

start_interface(os.path.abspath(os.curdir) + os.path.sep + "access_token.txt")
