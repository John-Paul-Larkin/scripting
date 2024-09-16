# John Paul Larkin
# C00001754
# Scripting Lab one - 15/9/24

# This function adds two numbers and prints the result
def add(num_1, num_2):
    # Calculate the sum of num_1 and num_2
    total = num_1 + num_2
    print(total)

# This function divides two numbers and returns the result   
def divide(num_1, num_2):
    # Define a function that divides two numbers and returns the result
    if num_2 == 0:
        return 0
    else:
        return num_1 / num_2

# This function subtracts two numbers entered by the user
def subtract():
    num_1 = input('Enter the first number: ')
    num_2 = input('Enter the second number: ')
    # Convert the input strings to integers and subtract them
    result = int(num_1) - int(num_2)
    print(result) 

if __name__ == "__main__":
    add(2,4)
    add(7,9)
    
    divide_result = divide(5,2)
    print(divide_result)

    subtract()
    
    
""""
ZeroDivisionError: division by zero
Occurred when I entered 0 as the second number in the divide function.
Fixed by adding a condition to check if the second number is 0 before dividing.
if it is 0, the function returns 0.

TypeError: unsupported operand type(s) for -: 'str' and 'str'   
Occurred when I tried to subtract two strings in the subtract function.
Fixed by converting the strings to integers before performing the subtraction.
"""