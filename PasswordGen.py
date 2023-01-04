#importing secrets and string library

import secrets
import string


letters = string.ascii_letters
numbers = string.digits
symbols = string.punctuation

#concatenate the above to get the full_password
#with letter (both lowercase and uppercase)
#with symbols
full_pass = letters+ numbers+ symbols



# The generated password must be have atleast a length of 12

password_length=12

# Now we generate the password 

fname,lname = input("Enter your first and last name to obtain your unique password  :").split()


genpasswd = ''  
for p in range(password_length):
    genpasswd +=''.join(secrets.choice(full_pass))

   

print(f"Hello  {fname} {lname} your unique password is  :"+genpasswd)