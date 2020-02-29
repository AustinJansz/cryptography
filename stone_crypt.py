import string                                                   # Use of ascii letter function
import math                                                     # Use of square root function

############################################################################################################
# Function source: https://codereview.stackexchange.com/questions/158925/generate-nth-prime-number-in-python 
def nth_prime(n):                                                   # Function to find the nth prime
    prime_list = [2]                                      
    num = 3                                                    
    while len(prime_list) < n:
        for p in prime_list:
            if num % p == 0:
                break
        else:
            prime_list.append(num)
        num += 2
    return prime_list[-1]
############################################################################################################

def key_handler(formatted_key, content_length, key_sum):            # Function to perform key expansion
    key_prime = 0
    i = 0
    j = 0
    key_prime = nth_prime(int(math.sqrt(key_sum)))                  # Selects prime based on the square root of the key sum
    key_letter = list(string.ascii_letters)[key_prime%52]           # Selects letter from the possbile ascii letters
    key_prime_hex = format(key_prime, 'x')                          # Defines a hex value via the prime number
    while i < len(list(str(key_prime_hex))):
        formatted_key.append(ord(list(str(key_prime_hex))[i]))      # Appends each character from the hex value to the key
        i += 1
    formatted_key.append(ord(key_letter))                           # Appends the "key letter" to the key
    original_key = formatted_key                                    # Creates a copy of the key for the purposes of duplication
    while len(formatted_key) < content_length:                      # Expand the key in a cyclical fashion until the length of the content
        formatted_key.append(original_key[j%(len(original_key))])
        j += 1
    return formatted_key                                            # Return the value of the expanded key

def format_input(raw_content, raw_key):                             # Function to handle all raw input from the user
    i = 0   
    j = 0
    ord_content = []                                                # Initialize lists to carry the mutated user input
    ord_key = []
    key_sum = 0                                                     # Variable to track the total length of the key
    content = list(raw_content)                                     # Parses the user's message and key as a list, new item at each character
    key = list(raw_key)                                         
    while i < len(content):                                         # Loop to append the value from the user's message to the ord_content list
        ord_content.append(ord(content[i]))
        i += 1
    while j < len(key):                                             # Loop to append the value from the user's key to the ord_key list
        key_sum += ord(key[j])                                      # Adds the sum of the current character to the running key sum
        ord_key.append(ord(key[j]))
        j += 1
    ord_key = key_handler(ord_key,len(ord_content),key_sum)         # Use the key handler to get an expanded key
    return ord_content, ord_key                                     # Return the ord_content and ord_key lists

def paired_reversal(list_contents):
    l_list_contents = list_contents[:len(list_contents)//2]         # Makes a list for both the left and right halves of a list
    r_list_contents = list_contents[len(list_contents)//2:]
    l_list_contents.reverse()                                       # Reverse both halves of the list       
    r_list_contents.reverse()
    list_contents = l_list_contents + r_list_contents               # Concatenates both halves (1,2,3,4,5,6 -> 3,2,1,6,5,4)
    return list_contents

def encrypt_message(raw_plaintext, raw_key):                        # Function to preform the encryption (differs from decryption)
    i = 0
    ord_plaintext,ord_key = format_input(raw_plaintext,raw_key)     # Use the formatter to get the correctly formatted plaintext and key
    ciphertext = []                                                 # Initialize a list to carry the ciphertext
    while i < len(ord_plaintext):                                   # Loop to XOR the key values and apply a shift to the output (alters printability)
        chipherchar = int(str(int(ord_plaintext[i]) ^ int(ord_key[i]))) + 200
        ciphertext.append(chr(chipherchar))                         # Appends the character at the position of the xor + shift to the ciphertext                    
        i += 1
    ciphertext = paired_reversal(ciphertext)                        # Uses the reversal function to scramble the ciphertext
    ciphertext_str = ''.join(ciphertext)                            # Creates a string with each of the elements from the ciphertext
    return ciphertext_str                                           # Return ciphertext string

def decrypt_message(raw_ciphertext, raw_key):                       # Function to preform the decryption
    i = 0
    ord_ciphertext,ord_key = format_input(raw_ciphertext,raw_key)   # Use the formatter to get the correctly formatted ciphertext and key
    plaintext = []                                                  # Initialize a list to carry the plaintext
    ord_ciphertext = paired_reversal(ord_ciphertext)                # Uses the reversal function to undo that of the encryption
    while i < len(ord_ciphertext):                                  # Loop to de-shift the values and XOR them with expanded key
        cipher_input = ord_ciphertext[i] - 200
        xor = int(str(int(cipher_input) ^ int(ord_key[i])))
        plaintext.append(chr(xor))                                  # Appends the character at the position of the de-shift + xor to the plaintext
        i += 1
    plaintext_str = ''.join(plaintext)                              # Creates a string with each of the element from the plaintext
    return plaintext_str                                            # Return plaintext string

def user_input():                                                   # Function to handle all user input and output
    user_valid_selection = False                                    # Initialize booleans for correct data entry
    user_valid_16B_string = False
    while not user_valid_selection:                                 # Loop until the user correctly selects encrypt or decrypt
        encrypt_decrypt = input("Encrypt [1] or decrypt [2]?: ")    # Prompt user to select one of the options
        
        # ENCRYPTION
        if encrypt_decrypt == '1':                                  # Option selected to encrypt
            user_file_input = input("File input? [y/n]: ")          # Asks if the user would like to select a file for encryption
            if user_file_input == 'y':
                file_location = input("Path to the file: ")         # Prompts for a path to the input file
                with open(file_location, 'r') as file:              # Open the file and parse contents to a string (replace newlines with spaces)
                    raw_plaintext = file.read().replace('\n', ' ')
            else:
                raw_plaintext = input("Enter your message: ")       # Prompts the user to manually enter a message (alternative to file entry)
            while not user_valid_16B_string:                        # Loops until the user has entered a 16 character key (restriction could be removed)
                raw_key = input("Key: ")                           
                if len(raw_key) == 16:
                    user_valid_16B_string = True
            user_file_input = input("Output to a file? [y/n]: ")    # Prompts the user to select write to file or output to console
            cipher = encrypt_message(raw_plaintext,raw_key)         # Calls encryption function to create ciphertext
            if user_file_input == 'y':
                file_location = input("Path to the file: ")         # Prompts the user to enter a path to save the ciphertext
                with open(file_location, 'w') as file:
                    file.write(cipher)                              # Writes cipher to file
            else:
                print(cipher)                                       # Prints the ciphertext to the console (alternative to file output)
            user_valid_selection = True                             # Updates boolean to exit program
    
        # DECRYPTION
        elif encrypt_decrypt == '2':                                # Option selected to decrypt    
            user_file_input = input("File input? [y/n]: ")          # Asks if the user would like to select a file for decryption
            if user_file_input == 'y':                  
                file_location = input("Path to the file: ")         # Prompts for a path to a the input file
                with open(file_location, 'r') as file:              # Open the file and parse the contents to a string
                    raw_ciphertext = file.read().replace('\n', ' ')
            else:
                raw_ciphertext = input("Enter your message: ")      # Prompts the user to manually enter a message
            while not user_valid_16B_string:                        # Loops until the user has entered a 16 character key
                raw_key = input("Key: ")                            
                if len(raw_key) == 16:
                    user_valid_16B_string = True
            user_file_input = input("Output to a file? [y/n]: ")    # Prompts the user to select to write to file or output to console
            plaintext = decrypt_message(raw_ciphertext,raw_key)     # Calls decryption function to create plaintext
            if user_file_input == 'y':
                file_location = input("Path to the file: ")         # Promts the user to enter a path to save the plaintext
                with open(file_location, 'w') as file:
                    file.write(plaintext)                           # Writes plaintext to file
            else:
                print(plaintext)                                    # Prints the plaintext to the console
            user_valid_selection = True                             # Updates boolean to exit the program

user_input()