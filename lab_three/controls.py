# John Paul Larkin
# C00001754
# Scripting Lab three - 2/10/24

# Function to check if a number is odd or even
def odd_or_even(number):
    # Returns True if the number modulo 2 is 0, i.e. the number is even, else False
    return number % 2 == 0

# Function to return the maximum value from a list of values
def max(*values):
     # Sort the values in ascending order and store them in 'sorted_list'
    sorted_list = sorted(values)
    # Return the last (largest) value from the sorted list, by accessing with a negative index
    return sorted_list[-1]

def find_the_syntax_errors():
    CORRECT_CODE = 'print("hello")'
    broken_code = 'PrInt("hello)'
    
    # Initialize the total count of errors
    total_count_error = 0
    print(broken_code)
    # Loop until the user enters the correct code
    while True:
        # Prompt the user to enter the fixed code
        fixed_code = input("Enter the fixed code: ")
        # Check if the fixed code is equal to the correct code
        if fixed_code == 'print("hello")':
            # If it is, break out of the loop
            print("Correct")
            print(f"Total number of errors: {total_count_error}")
            break
        else:
            # To count the number of errors
            error_count = 0
        
            # Compare the fixed code with the correct code character by character
            # loop until the end of the shortest string
            for i in range(min(len(fixed_code), len(CORRECT_CODE))):
                if fixed_code[i] != CORRECT_CODE[i]:
                    error_count += 1
        
        # Account for length difference as errors
        error_count += abs(len(fixed_code) - len(CORRECT_CODE))
        total_count_error += error_count 
        print(f"Number of errors: {error_count}")
        print("Try again!") 
    
        

if __name__ == "__main__":
    is_odd_or_even = odd_or_even(5)
    print(is_odd_or_even)
    
    max_num = max(9,7,6)
    print(max_num)
    
    max_num = max(8,5)
    print(max_num)
    
    find_the_syntax_errors()
    
    
    



# ERRORS ############
#     sorted = values.sort()
#     AttributeError: 'tuple' object has no attribute 'sort'

#     def max(*values):
#     values is a tuple, and tuples tuples are immutable and do not have a sort method.
#     I instead used the sorted function to return a list
