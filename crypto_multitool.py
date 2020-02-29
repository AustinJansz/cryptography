from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import keywrap
from cryptography.hazmat.primitives import hashes
from PIL import Image                                                                               # Image data reading and writing
import os
import random
import string

# Global Variables
# ----------------
ascii_characters = list(string.ascii_letters) + list(string.digits)                                 # Generates a list with lowercase + upercase letters + digits

# STEGANOGRAPHY TOOLS ---------------------------------------------------------------------------------------------------------------------------------------------------
def read_image(image_path):                                                                         # Function to read the image data to a list
    img = Image.open(image_path)                                                                    # Open the image
    pixels = list(img.getdata())                                                                    # Parse the data to a list
    width, height = img.size                                                                        # Get the width and height
    return pixels, width, height

def write_image(pixels, width, height, output_image):                                               # Function to write new image
    img = Image.new('RGBA', (width,height))                                                         # Initialize a new image with mode RGBA (includes transparency)
    img.putdata(pixels)                                                                             # Writes the data to the image
    img.save(output_image)                                                                          # Save the output to the user defined path
    img.show()                                                                                      # Preview image
    return

def add_message(message,image_path,output_image):                                                   # Function to add message to pixel data
    content = [ord(x) for x in list(message)]                                                       # Parse all data from message to a list
    pixel_list, width, height = read_image(image_path)                                              # Read all data from image
    augmented_pixels = []                                                                           # New list to hold augmented pixels
    i = 0
    j = 0
    while i < len(pixel_list):                                                                      # Loop to iterate through all image pixels
        pixel=[]
        if pixel_list[i][3] == 0:                                                                   # Checks to see if pixel is transparent
            if j+2 < len(content):                                                                  # Checks to see if there are 3 remaining elements in the message
                pixel=(content[j],content[j+1],content[j+2],0)                                      # Writes 3 pieces of data to the pixel (RGB, A remains 0)
                augmented_pixels.append(pixel)
            elif j+1 < len(content):                                                                # Checks to see if there are 2 remaining elements in the message
                pixel=(content[j],content[j+1],0,0)                                                 # Writes 2 pieces of data to the pixel (RG, B and A remain 0)
                augmented_pixels.append(pixel)                                                      
            elif j < len(content):                                                                  # Checks to see if there is at least 1 remaining elements in the message
                pixel=(content[j],0,0,0)                                                            # Writes the last piece of data to the pixel's R channel (rest remain 0)
                augmented_pixels.append(pixel)
            else:
                pixel=pixel_list[i]                                                                 # If message is message is complete, continue to write original pixels
                augmented_pixels.append(pixel)
            j+=3
        else:
            pixel=pixel_list[i]                                                                     # If pixel is not transparent, do not alter it
            augmented_pixels.append(pixel)
        i+=1
    write_image(augmented_pixels,width,height,output_image)                                         # Write the entire list of augmented pixels to an image
    return augmented_pixels

def comparison(image_path_1,image_path_2,output_image):                                             # Function to compare images (2 input images, 1 output path)
    pixels_1, width, height = read_image(image_path_1)                                              # Get the data of both images
    pixels_2 = read_image(image_path_2)[0]
    difference_pixels = []                                                                          # Initialize variables to hold the image data and the found message
    message = ''
    if len(pixels_1) != len(pixels_2):                                                              # Check to see if the images are the same size
        print("Images not compatible")                                                              # If not the same size, the images cannot be compared
        return
    i = 0
    while i < len(pixels_1):                                                                        # Loop to systematically compare the values of each pixel
        R1,G1,B1,A1 = pixels_1[i]                                                                   # Retrieve the pixel data for each of the images in their channels
        R2,G2,B2,A2 = pixels_2[i]
        R_diff = abs(R1-R2)                                                                         # Gets the difference between the channel values (same=0)
        if R1 != R2:
            message += chr(R_diff)                                                                  # Appends the data to the message only if they are different
        G_diff = abs(G1-G2)
        if G1 != G2:
            message += chr(G_diff)
        B_diff = abs(B1-B2)
        if B1 != B2:
            message += chr(B_diff)
        if R_diff > 0 or G_diff > 0 or B_diff > 0:                                                  # Checks to see if there was a difference in any of the channels
            A_diff = 255                                                                            # Sets the 'difference' pixel to 100% opaque
        else:   
            A_diff = abs(A1-A2)                                                                     # Sets the transparency to their difference

        pixel_difference = (R_diff,G_diff,B_diff,A_diff)                                            # Creates a tuple with the composite pixels     
        difference_pixels.append(pixel_difference)                                                  # Adds the tuple to the list of pixels
        i += 1
    write_image(difference_pixels,width,height,output_image)                                        # Writes the pixel data to a new image
    return message                                                                                  # Return the message found

# KEY WRAPPING TOOLS ----------------------------------------------------------------------------------------------------------------------------------------------------
def random_key():                                                                                   # Function to programatically generate pseudo-random 16B keys
    key = ""
    i = 0
    while i < 16:
        key += random.choice(ascii_characters)                                                      # Append a pseudo random ascii character
        i += 1
    key = key.encode()                                                                              # Encode the final key to get its byte data
    return key

def user_keys():                                                                                    # Function to accept user keys of length 16
    key_1 = ''                                                                                      # Initialize key containers
    key_2 = ''
    while len(key_1) != 16:                                                                         # Continuously prompts for a key until the correct length is achieved
        key_1 = str(input("16 character key to be wraped: "))
    while len(key_2) != 16:
        key_2 = str(input("16 character key wrapper: "))
    key_1 = key_1.encode()                                                                          # Coversion of both keys to byte format
    key_2 = key_2.encode()
    return key_1, key_2

def wrap_unwrap(key_1,key_2):                                                                       # Function to wrap and unwrap keys
    backend = default_backend()
    wrapped_key = keywrap.aes_key_wrap(key_2,key_1,backend=backend)                                 # Wrap key 1 with key 2
    unwrapped_key = keywrap.aes_key_unwrap(key_2,wrapped_key,backend=backend)                       # Unwrapped the wrapped key with the key 2
    return wrapped_key, unwrapped_key

# HASHING TOOLS ---------------------------------------------------------------------------------------------------------------------------------------------------------
def generate_md5(raw_input):
    digest = hashes.Hash(hashes.MD5(), backend=default_backend())
    digest.update(str(raw_input).encode())                                                          # Function to uniformly create a md5 hash
    hash_value = digest.finalize()
    return hash_value  

def generate_sha(raw_input):                                                                        # Function to uniformly create a sha256 hash
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(str(raw_input).encode())
    hash_value = str(digest.finalize())
    return hash_value       

def md5_collider(raw_input):
    hash_set = ['','']                                                                              # Set a new list to hold the user's hash and the potential collider
    hash_set[0] = generate_md5(raw_input)                                                           # Save the hash to a list for future comparison
    print("Hash of input: " + str(hash_set[0]))
    collision_found = False
    characters=[]
    j = 0
    while not collision_found:
        characters.append(ascii_characters[j%len(ascii_characters)])                                # Cycles through ascii characters
        i = 0
        digest = hashes.Hash(hashes.MD5(), backend=default_backend())
        while i < len(characters):                                                                  # For every character of the list, update the hash
            digest.update(characters[i].encode())
            i += 1
        calculated_hash = digest.finalize()                                                         # Save the latest digest
        print(calculated_hash)
        hash_set[1] = calculated_hash
        if hash_set[0] == hash_set[1]:                                                              # Compare the hashes
            collision_found = True                                                                  # Break the loop and print the collison
        j += 1
    return characters

def sha_collider(raw_input):
    hash_set = ['','']                                                                              # List to hold the base hash and the found hash
    hash_set[0] = generate_sha(raw_input)                                                           # Generates a hash from the users input
    print("Hash of input: " + hash_set[0])
    collison_found = False
    i = 0
    while not collison_found:
        hash_set[1] = generate_sha(i)                                                               # Iterates through numbers until a collision is found
        if hash_set[0] == hash_set[1]:
            collision = i
            collison_found = True                                                                   # Breaks loop once collision is found
        i += 1
    return collision

# USER EXPERIENCE -------------------------------------------------------------------------------------------------------------------------------------------------------
def user_input():                                                                                   # Function to supply the user interaction
    print("WELCOME TO THE SWISS ARMY TOOL SUITE\n----------------------------------")
    print("Modules:\n" \
        + "Steganography Tools---------------------\n" \
        + "[1] Message-in-Picture:\t\tAdd a message behind a picture's transparent pixels\n" \
        + "[2] Comparison:\t\t\tCompare two images to find hidden messages\n\n" \
        + "Key Wrapping----------------------------\n" \
        + "[3] Standard Wrapper:\t\tWrap keys with a defined key\n" \
        + "[4] Random Wrapper:\t\tWrap keys with a random wrapping key\n\n" \
        + "HASH Collider---------------------------\n" \
        + "[5] MD5 Collider:\t\tFind collisions for a provided string\n" \
        + "[6] SHA256 Collider:\t\tFind the input of a hash function with bruteforce attack\n\n" \
        + "[0] Exit program\n")
    input_valid = False                                                                             # Module selection validity tracker
    while not input_valid:
        module = input("Module: ")                                                                  # Prompt for module selection
        try:                                                                                        # Try statement to check if the user entry can be parsed
            module_select = int(module)
            if module_select == 0:
                return
            elif module_select > 0 and module_select < 7:                                           # Check user input against value modules
                input_valid = True
        except:
            input_valid = False

    # STEGANOGRAPHY TOOLS
    if module == '1':                                                                               # Module 1: MESSAGE-IN-PICTURE hider
        print("Tool information")
        print("- Accepts an image with transparent areas and adds a message behind them\n" \
            + "- Using a loop, this module selects creates lists of pixels and searches for transparent data\n" \
            + "- These spaces are stripped apart and use the RGB channels to include new data\n\n")
        message = input("Message: ")                                                                # Prompt the user for the secret message
        image_path = input("Path to input image: ")                                                 # Prompt the user for the path to the input image
        output_image = input("Path to output image: ")                                              # Prompt the user for the path of the output image
        add_message(message,image_path,output_image)                                                # Alteration of the image with the hidden message
    elif module == '2':                                                                             # Module 2: COMPARISON of images
        print("Tool information")
        print("- Accepts two images, one base image, and one suspected of hiding secrets\n" \
            + "- Using a double loop, this module compares the images, byte-by-byte to create a new image\n" \
            + "- This image clearly shows where image data has been tampred\n" \
            + "- Lastly, it parses all the differences and attempts to form a message string\n\n")
        image_path_1 = input("Path to the base image: ")                                            # Prompt the user for the base image
        image_path_2 = input("Path to the comparison image: ")                                      # Prompt the user for the suspected altered image
        output_image = input("Path to output composite image: ")                                    # Prompt the user for the path of the output image
        message = comparison(image_path_1,image_path_2,output_image)                                # Compare images
        if message != '':                                                                           # Check to see if a message was found between the images
            output_message = input("Save message to file? [Y/N]")                                       
            if output_message == 'Y' or output_message == 'y':                                      # Check to see if the user would like to save the message to a file
                output_path = input("Path to message output file: ")                                # Prompt the user to enter a path to save the massege to file
                with open(output_path, 'w') as file:                                                # Open/create file to store the message
                    file.write(message)
            else:
                print(message)                                                                      # Print the found message
        else:
            print("Message not found")                                                              # Inform the user that message was not found

    # KEY WRAPPING TOOLS
    elif module == '3':
        print("- Accepts two keys, one base key that requires extra protection, and one key to wrap it in\n" \
            + "- Wrapping a key works as an extra layer of security when transporting a key\n" \
            + "- This makes use of the AES encryption algorithm\n\n")
        key_1, key_2 = user_keys()
        print("\n[Key 1 || Key 2]: [" + str(key_1) + " || " + str(key_2) + "]")
        wrapped_key, unwrapped_key = wrap_unwrap(key_1, key_2)                                      # Call the function to get the user's properly formatted keys
        print("Key once wrapped: " + str(wrapped_key))                                              # Display formulated data
        print("Key after unwrapping: " + str(unwrapped_key))
    elif module == '4':
        print("- Accepts one base key and generates a pseudo-random key to wrap it in\n" \
            + "- Wrapping a key works as an extra layer of security when transporting a key\n" \
            + "- The random key is 16 characters in length and is built from printable characters\n\n")
        key_1 = '' 
        while len(key_1) != 16:                                                                     # Continuously prompts for a key until the correct length is achieved
            key_1 = str(input("16 character key to be wraped: "))
        key_1 = key_1.encode()                                                                      # Coversion of both keys to byte format
        key_2 = random_key()
        print("\n[Key 1 || Key 2]: [" + str(key_1) + " || " + str(key_2) + "]")
        wrapped_key, unwrapped_key = wrap_unwrap(key_1, key_2)                                      # Call the function to get the user's properly formatted keys
        print("Key once wrapped: " + str(wrapped_key))                                              # Display formulated data
        print("Key after unwrapping: " + str(unwrapped_key))

    # HASH TOOLS
    elif module == '5':
        print("- Accepts one message as input and creates an MD5 hash (128 bit)\n" \
            + "- The program then proceeds to append each printable character to a hash and checks if a collision is found\n" \
            + "- MD5 is susceptible to collisions and has since been depricated as it only supports 128 bits\n\n")
        raw_data = input("Enter a message to be hashed: ")
        collision = md5_collider(raw_data)                                                          # Call the function to brute force the user's message
        print("Collision found with the following characters: " + ''.join(collision))
    elif module == '6':
        print("- Accepts an integer number and creates a SHA256 hash (256 bit)\n" \
            + "- The program iterates through numbers until it finds the source of the hash\n" \
            + "- Hashes are meant to be a one-way operation thus you should not normally be able to find the source given a hash\n" \
            + "- SHA256 still has yet to be broken however this program only works with integer numbers, lowering the require cycles\n\n")
        input_valid = False
        while not input_valid:
            raw_data = input("Number to hash: ")                                                    # Get the user's input and verify that it is a number
            try:
                int_data = int(raw_data)
                input_valid = True
            except:
                input_valid = False
        collision = sha_collider(int_data)                                                          # Call the function to find the input for the SHA256 hash
        print("Collision found with the following number: " + str(collision))          

user_input()