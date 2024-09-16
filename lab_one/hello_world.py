# John Paul Larkin
# c00001754
# Scripting Lab one - 15/9/24

print('hello world')

# This function takes a parameter 'entered_name' and prints a personalized greeting.
def hello(entered_name):
    # Prints a greeting with the user's entered name.
    print('hello to you', entered_name)    
    
if __name__ == '__main__':
      # Prompts the user to input their name and stores it in the variable 'entered_name'.
    entered_name = input('Please enter your name:')
    hello(entered_name)