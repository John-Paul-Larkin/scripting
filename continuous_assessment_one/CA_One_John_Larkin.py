# John Paul Larkin
# C00001754
# Scripting Continuous Assessment One
# 2/12/24

import random


g_locations = {
    'Tower': {'north': 'Throne Room', 'east': 'Armory', 'south': 'Dungeon', 'item': 'map'},
    'Throne Room': {'south': 'Tower', 'item': 'crown'},
    'Armory': {'west': 'Tower', 'north': 'Library', 'item': 'sword'},
    'Library': {'south': 'Armory', 'item': 'spellbook'},
    'Dungeon': {'north': 'Tower', 'item': 'dragon'}
}

def show_game_options() -> None:
    # Print the game options - escape chars needed for "
    print(
        "The 'Knight in the Kingdom', a textual \"Adventure Game\"\n"
        "===================\n"
        "Commands:\n"
        "go [north|south|east|west] - Move in the specified direction\n"
        "get [item] - Pick up an item\n"
        "inspect room - See the items in the current room\n"
        "inspect inventory - See the items in your inventory"
    )


def show_status( current_location: str,  locations: dict ) -> None:
    print_in_color(f"You are in the {current_location}.")
    # The allowed directions are all the keys in the current location
    allowed_directions = locations[current_location].keys()
    # apart from the item key, which needs to be removed
    allowed_directions = [dir for dir in locations[current_location].keys() if dir != 'item']
    # join them into a string with spaces between them for printing
    print(f"Direction allowed are {' '.join(allowed_directions)}")
    

def inspect_inventory( inventory: list ) -> None:
    # If the inventory is empty, let the user know
    if not inventory:
        print_in_color("Your inventory is empty")
        return
    print_in_color("Current inventory : \n")
    # Print each item in the inventory
    for item in inventory:
        print(f" - {item} ")

def inspect_location( current_location: str,  locations: dict ) -> None:
    # Get the item in the current location
    item = locations[current_location].get('item')
    # If there is no item, let the user know
    if not item:
        print_in_color(f"There is nothing to see here")
        return
    # but if there is an item
    print_in_color(f"In this room I see {item}")

        
def get_command() -> tuple:
    # Keep asking the user for a command until they enter a valid one
    while True:
        # Prompt the command from the user - convert to lowercase and strip any leading or trailing whitespace
        print_in_color("Enter your command: ")
        command = input().lower().strip()
        # Split the command into words
        words = command.split(' ')
        # Check if the command is valid 
        # It must have exaclty two words, the first must be a valid action 
        if len(words) != 2 or words[0] not in ['go', 'get', 'inspect'] :
            print("Invalid command. Please enter a command with two words separated by space.")
            continue
        # Return the two words/ command as a tuple
        return tuple(words)
       
def move_to_next_location( current_location : str, target:str, locations:dict) -> str:
    # If the target direction is not a valid key for the current location
    if target not in locations[current_location]:
        # let the user know
        print(f"You cannot move to {target} from {current_location}")
        # and stay on the current location
        return current_location
    
    # Otherwise, move to the next location
    current_location = locations[current_location][target]
    print(f"You have moved to the {current_location}")
    return current_location
    
def pickup_item(target: str, inventory: list, current_location: str, locations:dict) -> None:
    # If the target item is not in the current location
    if target != locations[current_location]['item']:
        # let the user know
        print_in_color(f"Item {target} is not on {current_location}")
        return
    
    # Otherwise, add the item to the inventory 
    inventory.append(target)
    # and remove it from the current location
    locations[current_location].pop('item')
    # let the user know what they have picked up
    print_in_color(f"You have picked up the item {target}")
    # and show the inventory
    print(f"Your inventory is now: {(' '.join(inventory))}")
    

# Helper function to print text in a given color
# Make the users moves easier to read
def print_in_color(text):
    print(f"\n\033[94m{text}\033[0m")
    #  print(f"\033[94m{text}\033[0m", end='')


def game_mainloop(first_location: str, locations: dict) -> bool:
    current_location = first_location
    inventory: list = []

    show_game_options()

    while True:
        show_status(current_location, locations)
        
        # Get the player's next action
        move = get_command()

        if move:
            action, target = move

            if action == "go":
                current_location = move_to_next_location( current_location, target, locations)

            elif action == "get":
                pickup_item(target, inventory, current_location, locations)
 
            elif action == "inspect":
                if target == "inventory":
                    inspect_inventory(inventory)
                elif target == "room":
                    inspect_location(current_location, locations)
                else:
                    print("Cannot inspect that")

        # Note - I have removed the invalid command message as it is not required
        # it is handled by the get_command function - which expects a tuple returned
        # else:
        #     print("Invalid command. Try 'go [direction]', 'get [item]', or 'inspect [room/inventory]'.")

        if current_location == 'Throne Room' and 'crown' in inventory and 'sword' in inventory:
            # Winning condition
            print("Congratulations! You have claimed the throne with the crown and the sword!")
            return True
        
        if 'item' in locations[current_location] and locations[current_location]['item'] == 'dragon':
            # Losing condition: to be improved
            if 'sword' in inventory:
                print("You have defeated the dragon with your sword!")
                continue
            elif 'spellbook' in inventory:
                print("You have defeated the dragon with your spellbook!")
                continue
            
            print("The dragon has defeated you... Game Over!")
            return False
        
        
def randomly_distribute_items() -> dict:
    
    # I ran out of time to implement this function correclty
    # The rooms loop back to themselves

    locations = ['Tower', 'Throne Room', 'Armory', 'Library', 'Dungeon']
    items = ['map', 'crown', 'sword', 'spellbook', 'dragon']
    directions = ['north', 'south', 'east', 'west']

    # randomly shuffle the locations and items in place
    random.shuffle(locations)
    random.shuffle(items)   
    
     # Create the random_locations dictionary
    random_locations: dict = {}
    
    # Iterate over the locations
    for location in locations:
        # Create a new dictionary for the current location
        random_locations[location] = {}

        # Assign between 1 and 4(ie number of directions) random directions to each location
        random_directions = random.sample(directions, random.randint(1, len(directions)))
        # Iterate over the directions -
        for direction in random_directions:
            # Link to another location 
            # HERE I need to ensure the location does not loop back to itself
            target_location = random.choice([l for l in locations if l != location])
            random_locations[location][direction] = target_location
    
    return random_locations
    
    
if __name__ == "__main__":  
    
    random_locations = randomly_distribute_items()
    
    # Run the game
    if game_mainloop('Tower', g_locations):
        print("Congratulations! You have claimed the throne with the crown and the sword!")
    else:
        print("Better luck next time!")
