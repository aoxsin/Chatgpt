import openai
import json
import os
import argparse  # Import argparse here
from colorama import init, Fore

# Initialize colorama for colored output
init(autoreset=True)

# Define a file where API keys will be stored
API_KEYS_FILE = "api_keys.json"

# Load API keys from the file (or an empty list if the file does not exist)
def load_api_keys():
    if os.path.exists(API_KEYS_FILE):
        with open(API_KEYS_FILE, 'r') as file:
            api_keys = json.load(file)
    else:
        api_keys = []
    return api_keys

# Function to run the conversation with the API keys
def run_conversation(prompt, api_keys):
    for i, api_key in enumerate(api_keys):
        openai.api_key = api_key
        try:
            # Make an API call using the provided prompt
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",  # Use appropriate model
                messages=[{"role": "user", "content": prompt}]
            )
            print(f"K{i+1}: {response['choices'][0]['message']['content']}\n")
            break  # Stop once a valid key has worked
        except openai.error.RateLimitError:
            print(f"{Fore.RED}API Key K{i+1} is rate-limited.")
            continue  # If rate-limited, try the next key
        except Exception as e:
            print(f"{Fore.RED}Error with API Key K{i+1}: {str(e)}")
            continue  # If any other error occurs, try the next key

# Function to check the validity of each API key
def check_api_keys(api_keys):
    for i, api_key in enumerate(api_keys):
        openai.api_key = api_key
        try:
            # Check the API key by sending a test request
            openai.ChatCompletion.create(
                model="gpt-4o-mini",  # You can change this to your model
                messages=[{"role": "user", "content": "Hello"}]
            )
            print(f"{Fore.GREEN}API Key K{i+1} is valid")
        except openai.error.RateLimitError:
            print(f"{Fore.RED}API Key K{i+1} is rate-limited")
        except Exception:
            print(f"{Fore.RED}API Key K{i+1} is invalid")

# Function to load or interactively add API keys
def load_or_add_api_keys():
    api_keys = load_api_keys()

    if len(api_keys) > 0:
        print(f"You already have the following API keys saved:")
        for i, key in enumerate(api_keys, start=1):
            print(f"  Key {i}: {key[:10]}...")  # Show first 10 characters of the key for security

    num_keys_to_add = int(input("How many API keys you want to insert (1-5): "))
    
    for i in range(num_keys_to_add):
        api_key = input(f"Please enter API key {len(api_keys) + 1}: ")
        api_keys.append(api_key)

    save_api_keys(api_keys)
    return api_keys

# Function to save API keys to a file
def save_api_keys(api_keys):
    with open(API_KEYS_FILE, 'w') as file:
        json.dump(api_keys, file)
    print("API keys saved to file.")

# Argument parser for handling flags
def parse_args():
    parser = argparse.ArgumentParser(description="Interact with the OpenAI API using multiple keys.")
    parser.add_argument('prompt', type=str, nargs='?', help="The prompt to send to the OpenAI API.")
    parser.add_argument('-C', '--check', action='store_true', help="Check all API keys for validity.")
    parser.add_argument('-i', '--interactive', action='store_true', help="Interactively input API keys.")
    return parser.parse_args()

def main():
    args = parse_args()

    # Load API keys interactively if the -i flag is used
    if args.interactive:
        api_keys = load_or_add_api_keys()
    else:
        # Default to reading API keys from file if not interactive
        api_keys = load_api_keys()  # If you're not using environment variables, fall back to the config file

    if not api_keys:
        print(f"{Fore.RED}No API keys found. Please add your API keys using the -i flag.")
        return

    # If the --check flag is used, check API key validity
    if args.check:
        check_api_keys(api_keys)  # Check API keys for validity
    elif args.prompt:
        run_conversation(args.prompt, api_keys)  # Run conversation with the provided prompt

if __name__ == "__main__":
    main()
