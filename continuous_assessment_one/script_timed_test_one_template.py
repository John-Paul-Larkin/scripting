# John Paul Larkin
# C00001754
# Scripting Continuous Assessment One
# 2/12/24

g_locations = {
    'Tower': {'north': 'Throne Room', 'east': 'Armory', 'south': 'Dungeon', 'item': 'map'},
    'Throne Room': {'south': 'Tower', 'item': 'crown'},
    'Armory': {'west': 'Tower', 'north': 'Library', 'item': 'sword'},
    'Library': {'south': 'Armory', 'item': 'spellbook'},
    'Dungeon': {'north': 'Tower', 'item': 'dragon'}
}

def show_game_options() -> None:
    pass

def show_status( current_location: str,  locations: dict ) -> None:
    pass

def inspect_inventory( inventory: list ) -> None:
    pass

def inspect_location( current_location: str,  locations: dict ) -> None:
    pass

def get_command() -> tuple:
    pass

def move_to_next_location( current_location : str, target:str, locations:list) -> str:
    pass

def pickup_item(target: str, inventory: list, current_location: str, locations:dict) -> None:
    pass

def game_mainloop(first_location: str, locations: dict) -> bool:
    current_location = first_location
    inventory = []

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

        else:
            print("Invalid command. Try 'go [direction]', 'get [item]', or 'inspect [room/inventory]'.")

        if current_location == 'Throne Room' and 'crown' in inventory and 'sword' in inventory:
            # Winning condition
            print("Congratulations! You have claimed the throne with the crown and the sword!")
            break

        if 'item' in locations[current_location] and locations[current_location]['item'] == 'dragon':
            # Losing condition: to be improved
            print("The dragon has defeated you... Game Over!")
            break

