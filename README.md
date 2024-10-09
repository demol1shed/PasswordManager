A very basic password manager written purely in python. For first time entry a master username and a master password is necessary. The program supports endless users capable of managing their own passwords. 

__*Please do not forget logging in after you've signed in.*__

After signing in the user can save a new password with a password identifier (of which they should not forget) and the password itself. After saving the password the user can go back and demand the new password again or log out. Currently there is no way to retrieve the user's password in the case of them forgetting their master password/master username.

Master username, master password and password identifiers are hashed using sha256. User saved passwords are encrypted using AES symmetric encryption.  

__This program is insecure even though it has gone through all types of encrpytions/hashing as another user with access to your computer can delete or alter the files, their names or their contents which will result in the loss of your data. Please use at your own risk.__
