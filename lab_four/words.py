# John Paul Larkin
# C00001754
# Scripting Lab four - 6/10/24

def parse_name():
    # Ask the user to enter their full name
    full_name = input("Enter your full name (including middle): ")

    # Print the length of full_name string
    name_length = len(full_name)
    print(f"The length of the name is {name_length} characters")

    # Split the full name into a list of words based on the space character
    name_parts = full_name.split(" ")
    
    # Print the three parts of the name
    print(f"First name: {name_parts[0]}")
    print(f"Middle name: {name_parts[1]}")
    print(f"Last name: {name_parts[2]}")
    
def contains_word(sentence, word):
    # Check if the word is in the sentence
    if word not in sentence:
        print('not found')
    else:
        # Use the count() method to find how many times the word appears in the sentence
        count = sentence.count(word)
        # Print the result
        print(f"The word {word} appears {count} times in {sentence}")
  
def swap_gender_to_female(sentence):
    # Split the sentence into a list of words
    word_list = sentence.split(" ")
    
    # Iterate through the word_list by index
    for i in range(len(word_list)):
        # If the word is 'he', replace it with 'she' in the array
        if word_list[i] == 'he':
            word_list[i] = 'she'
        # If the word is 'him', replace it with 'her' 
        elif word_list[i] == 'him':
            word_list[i] = 'her'
        # If the word is 'his', replace it with 'hers'
        elif word_list[i] == 'his':
            word_list[i] = 'hers'
        # If the word is 'himself', replace it with 'herself'
        elif word_list[i] == 'himself':
            word_list[i] = 'herself'
    
    # Join the modified word_list back into a single string (sentence) with spaces between words
    sentence = " ".join(word_list)
    # Print the modified sentence
    print(sentence)
    
      

if __name__ == "__main__":  
    parse_name()
    contains_word('the quick brown fox jumps over the lazy dog', 'fox')
    TEST_SENTENCE = "Dibbler liked to describe himself as a merchant adventurer; everyone else liked to describe him as an itinerant pedlar whose money-making schemes were always let down by some small but vital flaw, such as trying to sell things he didn't own or which didn't work or, sometimes, didn't even exist."
    swap_gender_to_female(TEST_SENTENCE)