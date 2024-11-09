# John Paul Larkin
# C00001754
# Scripting Lab six - part one
#  9/11/24


import json

FILE_NAME = "users.txt"

def read_user_list_from_file():
    # Check if the file exists before trying to read it
    try:
        # Try to open and read the file
        with open(FILE_NAME, "r") as file:
            user_list = json.load(file)
    except FileNotFoundError:
        # If file doesn't exist, initialise an empty array
        user_list = []
    return user_list


def does_username_exist(username, user_list):
    # Check if the username already exists in the user list
    # any() returns True if any element of the iterable(user_list) is true
    return any(user["username"] == username for user in user_list)


def sign_up():
    user_details = {}

    # Ask the user for their details - strip() removes any leading or trailing whitespace
    user_details["name"] = input("Enter your name: ").strip()
    user_details["username"] = input("Enter your username: ").strip()
    user_details["password"] = input("Enter your password: ").strip()
    
    user_list = read_user_list_from_file()
    
    if does_username_exist(user_details["username"], user_list):
        print("Username already exists, please try again")
    else:
        # If the username doesn't exist, add the user details to the user_list
        user_list.append(user_details)
        # opens a file - or creates, if it doesn’t exist 
        # by deafult, in the current working directory
        with open(FILE_NAME, "w") as file:
        # Write the user details to a file - in JSON format
          json.dump(user_list, file)
          
          

def login():
    # Ask the user for their username and password
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    user_list = read_user_list_from_file()

    # Find the user details for the given username
    user_details = next((user for user in user_list if user["username"] == username), None)
    
    # If the user details are not found, print an error message and return
    if user_details is None:
        print("Username not found")
        return
           
    # Check if the username and password are correct
    if user_details["username"] == username and user_details["password"] == password:
        print(f"Hello welcome back {user_details['name']}")
    else:
        print("Login failed")

if __name__ == "__main__":  
    
    # Loop until the user chooses to exit by entering 3
    while True:
        choice = input("Would you like to (1) Sign up, (2) Log in, or (3) Exit? ")
        
        if choice == "1":
            sign_up()
        elif choice == "2": 
            login()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

    
    