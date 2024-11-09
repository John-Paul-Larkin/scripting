# John Paul Larkin
# C00001754
# Scripting Lab six - part two
# 9/11/24

import json

POLL_FILE = "poll.txt"

def initialize_poll():
    # Initialize poll options, with all counts set to 0
    # Only done once when the program is first run - file doesn't exist
    poll_data = {
        "What is your favorite sport?": {
            "Soccer": 0,
            "Rugby": 0,
            "Hurling": 0,
            "Basketball": 0,
            "Football": 0,
            "Tennis": 0,
            "Skipping": 0,
            "Cycling": 0,
            "Swimming": 0,
            "Other": 0
        }
    }
    # Write initial poll data to the file
    with open(POLL_FILE, "w") as file:
        json.dump(poll_data, file)

def load_poll_data():
    # Try to load the poll data from the file
    try:
        with open(POLL_FILE, "r") as file:
            return json.load(file)
    # If the file doesn't exist, initialize the poll and then load the data again
    except FileNotFoundError:
        initialize_poll()
        return load_poll_data()

def save_poll_data(poll_data):
    # Write the poll data to the file
    with open(POLL_FILE, "w") as file:
        json.dump(poll_data, file)

def display_options(options):
    # Print the available options
    print("\nAvailable options:")
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")

def conduct_poll():
    # Load the poll data
    poll_data = load_poll_data()
    # The first key from the poll_data dictionary is the poll question
    question = list(poll_data.keys())[0]  
    # Get the options for the poll question
    options = list(poll_data[question].keys())
    
    print(f"\n{question}")
    display_options(options)
    
    while True:
        number_of_options = len(options)
        # Ask the user to enter the number of their choice
        try:
            choice = int(input(f"\nEnter the number of your choice (1-{number_of_options}): "))
            # If the choice is valid, break the loop
            if 1 <= choice <= len(options):
                selected_option = options[choice-1]
                break
            print(f"Invalid choice. Please select a number between 1 and {number_of_options}.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Update the count for selected option by adding 1
    poll_data[question][selected_option] += 1
    # Save the updated poll data to the file
    save_poll_data(poll_data)
    
    # Display results
    print("\nCurrent Poll Results:")
    for option, count in poll_data[question].items():
        print(f"{option}: {count} votes")

if __name__ == "__main__":
    while True:
        conduct_poll()
        # Ask the user if another person would like to vote- lower in case of Y or y
        another = input("\nWould another person like to vote? (y/n): ").lower()
        if another != 'y':
            break
    
    print("\nFinal Poll Results:")
    poll_data = load_poll_data()
    # Iterate through the poll data
    for question, results in poll_data.items():
        print(f"\n{question}")
        # Print the results for each option
        for option, count in results.items():
            print(f"{option}: {count} votes")
