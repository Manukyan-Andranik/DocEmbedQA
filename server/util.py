import re
import string

# Function to strip non-alphabetic characters from the beginning and end of a string
def strip_non_alpha(string, symbols= string.punctuation.split() + string.whitespace.split()):
    # Constructing regex pattern to match non-alphabetic characters at the beginning or end of the string
    pattern = '^[' + re.escape(''.join(symbols)) + ']+|[' + re.escape(''.join(symbols)) + ']+$'
    # Removing matched non-alphabetic characters and adding a period at the end
    return re.sub(pattern, '', string) + "."

# Function to print text centered within a certain width
def print_centered_text(text):
    # Calculating the width for the text and padding
    width = max(len(text) + 10, 30)
    padding = (width - len(text)) // 2 - 1
    start_end_line = '*' * width
    # Printing the centered text surrounded by asterisks
    print(start_end_line)
    print('*' + ' ' * padding + text + ' ' * padding + '*')
    print(start_end_line)

# Function to print a title with a specified padding
def print_title(title, padding=40):
    # Printing the title surrounded by dashes
    print("\n" + "-"*padding+title+"-"*padding)

# Function to parse a command into an action and parameters
def parse_command(command):
    command = command.strip()
    split_command = command.split(" ", 1)  
    action = split_command[0]  # Extracting the action from the command
    parameters = split_command[1].strip() if len(split_command) > 1 else None  # Extracting parameters if available
    return action, parameters
