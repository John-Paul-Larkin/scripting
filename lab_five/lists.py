# John Paul Larkin
# C00001754
# Scripting Lab five - 13/10/24


def even_or_odd():
    # Create three empty lista to store the entered numbers, the even numbers and the odd numbers
    numbers = []
    evens = []
    odds = []
    
    print('Please enter 10 numbers')
    # Loop 10 times to get 10 numbers from the user
    for i in range(10):
        number = int(input("Enter a number: "))
        # Append the number to the numbers list
        numbers.append(number)
    

    # For each number in the numbers list, check if it is even or odd and append it to the respective list  
    for number in numbers:
        if number % 2 == 0:
            evens.append(number)
        else:
            odds.append(number)

    # Print the list of even and odd numbersß
    print(f"The list of even numbers: {evens}")
    print(f"Odd numbers: {odds}")

def sort_fruits_alphabetically(fruits):
    # Sort the fruits list in alphabetical order
    # use str.lower to sort the list in a case-insensitive manner
    sorted_fruits = sorted(fruits, key=str.lower)
    # Print the sorted list
    print(sorted_fruits)

def combine_and_sort_lists(fruits, vegetables):
    # Combine the fruits and vegetables lists
    combined_list = fruits + vegetables
    # Sort the combined list in alphabetical order
    sorted_combined_list = sorted(combined_list, key=str.lower)
    # Print the sorted combined list
    print(sorted_combined_list)

def is_fruit_or_vegetable(item, fruits, vegetables):
    
    # Convert the item to lowercase for case-insensitive comparison
    item_lower = item.lower()
    
    # Create a new list where each fruit is converted to lowercase
    # Check if the item is in the new list
    if item_lower in [fruit.lower() for fruit in fruits]:
        print(f"{item} is a fruit")
    
    # Create a new list where each vegetable is converted to lowercase
    # Check if the item is in the new list
    elif item in [vegetable.lower() for vegetable in vegetables]:
        print(f"{item} is a vegetable")
    else:
        print(f"{item} is neither a fruit nor a vegetable")

if __name__ == "__main__":  
    even_or_odd()
    
    fruits = [ "cherry", "orange","apple", "Banana", "Grape", "strawberry", "pineapple", "mango"]
    sort_fruits_alphabetically(fruits)
    
    vegetables = [ "spinach", "potato", "Carrot", "broccoli", "tomato", "Cucumber", "lettuce", "pepper"]
    combine_and_sort_lists(fruits, vegetables)
    
    item = input("Enter a string: ")
    is_fruit_or_vegetable(item, fruits, vegetables)