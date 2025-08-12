# pico.py

import os
import requests
import json
import base64

# Base URL for GitHub API
GITHUB_API_URL = "https://api.github.com"
# Path to the file where the token will be stored
TOKEN_FILE = os.path.join(os.path.expanduser('~'), '.cirebon_token')
# Placeholder for the repository name
REPO_NAME = None 

# --- Helper functions ---

def _get_token():
    """Reads the token from the local file."""
    try:
        with open(TOKEN_FILE, 'r') as f:
            token = f.read().strip()
            if not token:
                print("Error: Token file is empty. Please run 'pico auth <key>' first.")
                return None
            return token
    except FileNotFoundError:
        print("Error: Token file not found. Please run 'pico auth <key>' first.")
        return None
    except Exception as e:
        print(f"Error: Failed to read token: {e}")
        return None

def _get_auth_headers():
    """Returns headers for GitHub API authentication."""
    token = _get_token()
    if token:
        return {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    return None

# --- Main functions for pico commands ---

def handle_pico_command(command, args):
    """
    Main dispatcher function for all pico commands.
    Parses the command and calls the corresponding function.
    """
    if command == "auth":
        auth(args)
    elif command == "logdown":
        logdown(args)
    elif command == "upload":
        upload(args)
    elif command == "download":
        download(args)
    elif command == "repo":
        repo(args)
    elif command == "rm":
        rm(args)
    elif command == "exit":
        print("Use `pico exit` to control the shell behavior.")
    else:
        print(f"Error: Unknown pico command '{command}'.")

def auth(args):
    """Saves the GitHub token to a local file."""
    if not args:
        print("Error: 'auth' requires a key.")
        return

    key = args[0]
    try:
        with open(TOKEN_FILE, 'w') as f:
            f.write(key)
        print("Success: Token saved successfully.")
    except Exception as e:
        print(f"Error: Failed to save token: {e}")

def logdown(args):
    """Deletes the token from the file for security."""
    if not args:
        print("Error: 'logdown' requires a key.")
        return
    
    key_to_check = args[0]
    stored_token = _get_token()

    if stored_token and key_to_check == stored_token:
        try:
            os.remove(TOKEN_FILE)
            print("Success: Token has been removed.")
        except Exception as e:
            print(f"Error: Failed to remove token file: {e}")
    else:
        print("Error: Provided key does not match the stored token or no token is stored.")


def upload(args):
    """Uploads a file to GitHub."""
    if not args:
        print("Error: 'upload' requires a filename.")
        return

def download(args):
    """Downloads a file from GitHub."""
    if not args:
        print("Error: 'download' requires a filename.")
        return

def repo(args):
    """Manages the current repository."""
    pass

def rm(args):
    """Deletes files from the repository."""
    if not args:
        print("Error: 'rm' requires arguments.")
        return
