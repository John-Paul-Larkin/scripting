# John Paul Larkin
# C00001754
# Scripting Lab nine
# 8/2/24

import sqlite3
import requests

import sqlite3
from datetime import datetime

# Import the matplotlib library to create the chart
import matplotlib.pyplot as plt

class Database:
    def __init__(self, db_name="star_wars.db"):
        # Connect to the database/ create it if it doesn't exist
        self.connection = sqlite3.connect(db_name)    
        # Create a cursor object
        self.cursor = self.connection.cursor()
    
    # Method which create a table if it doesn't exist
    def create_table(self, table_name):
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS {} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            gender TEXT NOT NULL,
            homeworld TEXT NOT NULL
        )
        '''
        # Pass the table name to the query when executing it
        self.cursor.execute(create_table_query.format(table_name))
        # Commit the changes to the database
        self.connection.commit()
      
    # Method which saves a single row of data to the database
    def save_data(self, table_name, name, gender, homeworld):
        insert_query = '''
            INSERT INTO {} (name, gender, homeworld) values (:name, :gender, :homeworld)
        '''
        # Pass the table name, along with the data to the query when executing it
        self.cursor.execute(insert_query.format(table_name), {'name': name, 'gender': gender, 'homeworld': homeworld})
        # Commit the changes to the database
        self.connection.commit()
    
    # Method which gets the specified columns of data from the database
    def get_data(self, table_name, cols):
        select_query = '''
            SELECT {} FROM {}
        '''
        self.cursor.execute(select_query.format(cols, table_name))
        # Return all fetched column data
        return self.cursor.fetchall()

    # Method which closes the connection to the database
    def close(self):
        self.connection.close()
  
# Fetch the data from the star wars API
def fetch_data():
    BASE_URL = "https://swapi.dev/api/people/"
    
    response = requests.get(BASE_URL)
    if response.status_code == 200:
        data = response.json()
    else:
        print(response.status_code)
        print("Failed to fetch data")
        exit()
    return data  
        
# Create a bar chart to display the gender distribution of the characters
def plot_data(data):
   # Create a dictionary to store the count of characters for each gender
    gender_counts = {}
    # Iterate through the data and count the number of characters for each gender
    for row in data:
        # Extract the gender from the row
        gender = row[1]
        # Increment the count of the gender
        gender_counts[gender] = gender_counts.get(gender, 0) + 1


    # Prepare data for the bar chart
    genders = list(gender_counts.keys())
    counts = list(gender_counts.values())

    # Plot the bar chart
    plt.figure(figsize=(8, 6)) 
    plt.bar(genders, counts, color='blue')
    plt.xlabel('Gender')
    plt.ylabel('Count')
    plt.title('Star Wars Characters Gender Distribution')
    plt.tight_layout()
    plt.show()
    


class Login:
    def __init__(self, db_name="users.db"):
        # Connect to (or create) the SQLite database
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        # Create the users table if it does not exist.
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT,
                login_count INTEGER,
                lastLogin TEXT
            )
        ''')
        # Commit any changes to the database
        self.connection.commit()

    def signup(self):
        # Allows the user to create a new account with a unique username
        while True:
            # Get the username from the user, and strip any whitespace
            username = input("Enter a username for signup: ").strip()
            # Check if username already exists.
            self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            # If the username already exists, print a message and ask the user to choose a new username
            if self.cursor.fetchone():
                print("Username already exists. Please choose a new one.")
            else:
                break
        # Get the password from the user, and strip any whitespace
        password = input("Enter a password: ").strip()

        # Insert new user with initial login_count 0 and lastLogin as None.
        self.cursor.execute(
            "INSERT INTO users (username, password, login_count, lastLogin) VALUES (?, ?, ?, ?)",
            (username, password, 0, None)
        )
        self.connection.commit()
        print("Signup successful! You can now log in.")

    def login(self):
        # Handles user login and provides post-login options.
        # Get the username from the user, and strip any whitespace
        username = input("Enter username: ").strip()
        # Get the password from the user, and strip any whitespace
        password = input("Enter password: ").strip()
        # Check if the username exists in the database
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = self.cursor.fetchone()

        # If the username does not exist, print a message and return
        if not user:
            print("Username does not exist. Please sign up.")
            return

        # If the password is incorrect, print a message and return
        if password != user[1]:
            print("Incorrect password.")
            return

        # user tuple: (username, password, login_count, lastLogin)
        # Save the old lastLogin and login_count values
        old_login_count = user[2]
        old_last_login = user[3]
        # Increment the login count
        new_login_count = old_login_count + 1
        # Get the current time and format it as a string 
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Update the user's login count and record the new login time.
        self.cursor.execute(
            "UPDATE users SET login_count = ?, lastLogin = ? WHERE username = ?",
            (new_login_count, current_time, username)
        )
        # Commit the changes to the database
        self.connection.commit()

        # Welcome message showing login count and last login time.
        if old_last_login:
            print(f"\nWelcome, {username}! You have logged in {new_login_count} times.")
            print(f"Your last login was on {old_last_login}.")
        else:
            print(f"\nWelcome, {username}! This is your first login.")

        # Provide additional options after a successful login.
        while True:
            print("\nWhat would you like to do next?")
            print("1. Change password")
            print("2. Delete account")
            print("3. Logout")
            option = input("Enter option number: ").strip()

            if option == "1":
                self.change_password(username)
            elif option == "2":
                # Confirm the deletion of the account - lower case y or n
                confirm = input("Are you sure you want to delete your account? (y/n): ").strip().lower()
                if confirm == 'y':
                    self.remove_account(username)
                    # Exit the menu after deletion.
                    break 
            elif option == "3":
                print("Logging out.")
                break
            else:
                print("Invalid option. Please try again.")

    # Mathod to allow a logged-in user to change their password.
    def change_password(self, username):
        new_password = input("Enter your new password: ").strip()
        self.cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
        self.connection.commit()
        print("Password updated successfully!")

    # Method to allow a logged-in user to delete their account.
    def remove_account(self, username):
        self.cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        self.connection.commit()
        print("Your account has been deleted successfully.")


def part_one():
    db = Database()
    # Create a table if it doesn't exist
    db.create_table("star_wars_characters")
    # Fetch the data from the star wars API
    star_wars_data = fetch_data()
    # Iterate through the fetched data and save it to the database
    for character in star_wars_data['results']:
        db.save_data("star_wars_characters", character.get('name'), character.get('gender'), character.get('homeworld'))
  
    data =  db.get_data("star_wars_characters", "name, gender, homeworld")   
    # Plot the data
    plot_data(data)
    
    # Close the database connection
    db.close()
    
def part_two():
    # Create a login object from the Login class
    login_system = Login()
    
    while True:
        print("\nPlease choose an option:")
        print("1. Signup")
        print("2. Login")
        print("3. Exit")
        option = input("Enter option number: ").strip()

        if option == "1":
            login_system.signup()
        elif option == "2":
            login_system.login()
        elif option == "3":
            print("Exiting program.")
            break
        else:
            print("Invalid option. Please try again.")
          
def main():
    # Part 1 - exercising with databases
    part_one()
    
    # Part 2 - login system
    part_two()

   
           
if __name__ == "__main__":  
    main()     