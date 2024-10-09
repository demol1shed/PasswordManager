import tkinter
import subprocess
from tkinter import ttk
from tkinter import *
from tkinter import messagebox
from hashlib import sha256
from typing import List
from cryptography.fernet import Fernet
import os.path


class UserManager:
    userPathFile = "usersSigned"
    hashedKey = sha256("key".encode("utf-8"))

    def __init__(self):
        if not os.path.isdir(f"{self.userPathFile}"):
            os.mkdir(f"{self.userPathFile}")

    def SignInCheck(self, _username) -> bool:
        if os.path.isfile(f"{self.userPathFile}/{_username}/{_username}.txt"):
            return True
        return False

    def SignInUser(self, _username, _password):
        if self.SignInCheck(_username):
            guiHandler.ThrowErr("Failure!", "User already exists")
            return
        if _username and _password:
            os.mkdir(f"{self.userPathFile}/{_username}")
            with open(f"{self.userPathFile}/{_username}/{_username}.txt", "x") as file:
                file.write(f"{_username},{_password}\n")
            self.username = _username
            self.password = _password
            guiHandler.ThrowInfo("Success!", "Signed in successfully")
        else:
            guiHandler.ThrowErr("Failure!", "Please enter a valid username or password")

    def LogInUser(self, _username, _password):
        if not self.SignInCheck(_username):
            guiHandler.ThrowErr("Failure!", "User does not exist")
            return
        if _username and _password:
            with open(f"{self.userPathFile}/{_username}/{_username}.txt", "r") as file:
                infoList = file.readline().split(',')
            if _password == infoList[1].strip():
                guiHandler.ThrowInfo("Success!", "You have successfully logged in")
                guiHandler.InitPostLoginScreen()
            else:
                guiHandler.ThrowErr("Failure!", "The password you have entered is incorrect")
        else:
            guiHandler.ThrowErr("Failure!", "Please enter a valid username or password")

    def ChkUserAcc(self, _username) -> bool:
        if not _username:
            guiHandler.ThrowErr("Failure!", "Please enter a valid username")
            return False
        if len(os.listdir(f"{self.userPathFile}/{_username}/")) > 1:
            return True
        return False


    def SavePassInfo(self, _username, passName, passToSave):
        if not passName and passToSave:
            guiHandler.ThrowErr("Failure!", "Invalid password name or password")
            return
        self.Encrypt(_username, passToSave, passName)
        guiHandler.ThrowInfo("Success!", "Your information has been saved successfully")

    def RetrievePassInfo(self, _username, passName):
        if not passName:
            guiHandler.ThrowErr("Failure!", "Invalid password name")
            return
        desiredPass = self.Decrypt(_username, passName)
        if not desiredPass:
            guiHandler.ThrowErr("Failure!", "Password could not be acquired")
            return
        guiHandler.ThrowInfo("Success!", f"Password: {desiredPass}")

    def Encrypt(self, _username, message: str, passName: str):
        key = Fernet.generate_key()
        fernet = Fernet(key)
        bMessage = str.encode(message)
        token = fernet.encrypt(bMessage)

        if os.path.isfile(f"{self.userPathFile}/{_username}/{passName}.txt"):
            with open(f"{self.userPathFile}/{_username}/{passName}.txt", "wb") as file:
                bToWrite = str.encode(f"{token.decode()}\n")
                file.write(bToWrite)
            self.SaveKey(_username, passName, key)

        with open(f"{self.userPathFile}/{_username}/{passName}.txt", "xb") as file:
            bToWrite = str.encode(f"{token.decode()}\n")
            file.write(bToWrite)
        self.SaveKey(_username, passName, key)

    def SaveKey(self, _username, passName, key: bytes):
        if os.path.isfile(f"{self.userPathFile}/{_username}/{passName}{self.hashedKey.hexdigest()}.txt"):
            with open(f"{self.userPathFile}/{_username}/{passName}{self.hashedKey.hexdigest()}.txt", "wb") as file:
                file.write(key)
            return

        with open(f"{self.userPathFile}/{_username}/{passName}{self.hashedKey.hexdigest()}.txt", "xb") as file:
            file.write(key)
            self.HideFile(_username, passName)

    def Decrypt(self, _username, passName: str) -> str:
        with open(f"{self.userPathFile}/{_username}/{passName}{self.hashedKey.hexdigest()}.txt", "rb") as file:
            key = file.read()
        with open(f"{self.userPathFile}/{_username}/{passName}.txt", "rb") as file:
            token = file.read()

        fernet = Fernet(key)
        sMessage = str(fernet.decrypt(token), 'utf-8')
        return sMessage

    def ReturnPasswordCount(self, _username) -> int:
        return int((len(os.listdir(f"{self.userPathFile}/{_username}")) - 1) / 2)

    def HideFile(self, _username, passName):
        subprocess.run(["attrib", "+H", f"{self.userPathFile}/{_username}/{passName}{self.hashedKey.hexdigest()}.txt"], check=True)

class GUIHandler:
    def __init__(self, root: Tk, mainFrame: ttk.Frame):
        self.usernameEntry = None
        self.passwordEntry = None
        self.password = StringVar()
        self.username = StringVar()
        self.passName = StringVar()
        self.passToSave = StringVar()
        self.root = root
        self.mainFrame = mainFrame

    def SaveButtonWrapper(self):
        hashedUsername = self.EncodeUP(self.username.get())
        hashedPassName = self.EncodeUP(self.passName.get())
        userManager.SavePassInfo(hashedUsername, hashedPassName, self.passToSave.get())

    def RetrieveButtonWrapper(self):
        hashedUsername = self.EncodeUP(self.username.get())
        hashedPassName = self.EncodeUP(self.passName.get())
        userManager.RetrievePassInfo(hashedUsername, hashedPassName)

    def EncodeUP(self, stringToHash: str) -> str:
        hashedStr = sha256(stringToHash.encode("utf-8"))
        return hashedStr.hexdigest()

    def SignInUser(self):
        userManager.SignInUser(self.EncodeUP(self.username.get()), self.EncodeUP(self.password.get()))

    def LogInUser(self):
        userManager.LogInUser(self.EncodeUP(self.username.get()), self.EncodeUP(self.password.get()))

    def InitFirstWindow(self):
        self.ClearWindow()
        self.InitLabels()
        self.InitEntries()
        self.InitButtons()

    def InitLabels(self):
        ttk.Label(self.mainFrame, text="Please enter your username and password").grid(column=0, row=0, sticky=N, pady=5)
        ttk.Label(self.mainFrame, text="Username").grid(column=0, row=1, sticky=W)
        ttk.Label(self.mainFrame, text="Password").grid(column=0, row=3, sticky=W)

    def InitEntries(self):
        self.usernameEntry = ttk.Entry(self.mainFrame, textvariable=self.username)
        self.passwordEntry = ttk.Entry(self.mainFrame, textvariable=self.password, show="*")
        entryList = [self.usernameEntry, self.passwordEntry]
        self.ClearEntryContents(entryList)

        self.usernameEntry.grid(column=0, row=2, pady=1, sticky=W)
        self.passwordEntry.grid(column=0, row=4, pady=1, sticky=W)

    def InitButtons(self):
        ttk.Button(self.mainFrame, text="Log in", command=self.LogInUser).grid(column=0, row=5, pady=5, sticky=W)
        ttk.Button(self.mainFrame, text="Sign in", command=self.SignInUser).grid(column=0, row=6, pady=5, sticky=W)

    def InitPostLoginScreen(self):
        self.ClearWindow()
        passCount = self.InitPassCount()
        passLabel = ttk.Label(self.mainFrame)
        passCountLabel = ttk.Label(self.mainFrame, text=f"{passCount} passwords exist")
        passCountLabel.grid(column=1, row=3, columnspan=2)
        passLabel.grid(column=1, row=1)
        passNameEntry = ttk.Entry(self.mainFrame, textvariable=self.passName)
        passNameEntry.grid(column=1, row=2, padx=5)
        self.ClearEntryContents([passNameEntry])
        ttk.Button(self.mainFrame, text="Save new password", command=self.InitNewPassScreen).grid(column=0, row=1, pady=10, padx=10)
        rButton = ttk.Button(self.mainFrame, text="Retrieve saved password")
        rButton.grid(column=0, row=2, pady=10, padx=10)
        self.ReturnToLastWindow(2)
        if userManager.ChkUserAcc(self.EncodeUP(self.username.get())):
            passLabel.config(text="Enter desired password name below")
            rButton.config(state=tkinter.NORMAL)
            rButton.config(command=self.RetrieveButtonWrapper)
        else:
            passLabel.config(text="Please save a password first")
            rButton.config(state=tkinter.DISABLED)

    def InitNewPassScreen(self):
        self.ClearWindow()

        passNameEntry = ttk.Entry(self.mainFrame, textvariable=self.passName)
        passNameEntry.grid(column=1, row=1)
        passEntry = ttk.Entry(self.mainFrame, textvariable=self.passToSave)
        passEntry.grid(column=1, row=2)
        entryList = [passNameEntry, passEntry]
        ttk.Label(self.mainFrame, text="Please enter the password name and the password itself").grid(column=0, row=0, columnspan=3, pady=5)
        ttk.Label(self.mainFrame, text="Password name").grid(column=0, row=1 ,padx= 5)
        ttk.Label(self.mainFrame, text="Password").grid(column=0, row=2, padx= 5)
        ttk.Button(self.mainFrame, text="Save", command=self.SaveButtonWrapper).grid(column=0, row=3, pady=10, columnspan=2)

        self.ClearEntryContents(entryList)
        self.ReturnToLastWindow(0)

    def ReturnToLastWindow(self, winIndex):
        # 0 for operations which when cancelled will not log out of the account.
        if winIndex == 0:
            ttk.Button(self.mainFrame, text="Cancel", command=self.InitPostLoginScreen).grid(column=2, row=3, pady=15, padx=5)
            return
        # 1 for just going back a frame
        # currently unused?
        if winIndex == 1:
            ttk.Button(self.mainFrame, text="Back").grid(column=2, row=3, pady=15, padx=5)
            return
        # 2 for logging out.
        if winIndex == 2:
            ttk.Button(self.mainFrame, text="Log out", command=self.InitFirstWindow).grid(column=0, row=3, pady=10, padx=10)
            return
        self.ThrowErr("Failure!", f"winIndex: '{winIndex}' does not exist")

    def ClearWindow(self):
        for widget in self.mainFrame.winfo_children():
            widget.destroy()

    def ClearEntryContents(self, entries: List[ttk.Entry]):
        for entry in entries:
            entry.delete(0, END)

    def InitPassCount(self):
        hashedUsername = self.EncodeUP(self.username.get())
        return userManager.ReturnPasswordCount(hashedUsername)

    @staticmethod
    def ThrowErr(title, text):
        messagebox.showerror(title, text)

    @staticmethod
    def ThrowInfo(title, text):
        messagebox.showinfo(title, text)

    @staticmethod
    def ThrowWarn(title, text):
        messagebox.showwarning(title, text)

def InitRoot() -> Tk:
    _root = Tk()
    _root.geometry("400x250")
    _root.title("demol1shed password manager")
    _root.resizable(False, False)
    _root.columnconfigure(0, weight=1)
    _root.rowconfigure(0, weight=1)
    return _root

def InitMainFrame(root: Tk) -> ttk.Frame:
    frame = ttk.Frame(root)
    frame.grid(column=0, row=0, sticky=(N, W, E, S))
    return frame

root = InitRoot()
mainFrame = InitMainFrame(root)

guiHandler = GUIHandler(root, mainFrame)
userManager = UserManager()

guiHandler.InitFirstWindow()

root.mainloop()
