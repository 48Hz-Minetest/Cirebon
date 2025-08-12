# pico.py

import os
import sys
import requests
import json
import base64

# Base URL for GitHub API
GITHUB_API_URL = "https://api.github.com"
# Path to the file where the token will be stored
TOKEN_FILE = os.path.join(os.path.expanduser('~'), '.cirebon_token')
# Path to the file where the current repository name is stored
REPO_CONFIG_FILE = os.path.join(os.path.expanduser('~'), '.cirebon_repo')

# Placeholder for the repository name
_current_repo = None 

# --- Helper functions ---

def _save_repo(repo_name):
    """Saves the current repository name to a local file."""
    try:
        with open(REPO_CONFIG_FILE, 'w') as f:
            f.write(repo_name)
    except Exception as e:
        print(f"Warning: Failed to save repository config: {e}")

def _load_repo():
    """Loads the current repository name from a local file."""
    global _current_repo
    try:
        with open(REPO_CONFIG_FILE, 'r') as f:
            _current_repo = f.read().strip()
    except FileNotFoundError:
        _current_repo = None
    except Exception as e:
        print(f"Warning: Failed to load repository config: {e}")
        _current_repo = None
    return _current_repo

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

def _get_repo_owner():
    """Returns the GitHub username for the token owner."""
    headers = _get_auth_headers()
    if not headers:
        return None
    try:
        response = requests.get(f"{GITHUB_API_URL}/user", headers=headers)
        response.raise_for_status()
        user_data = response.json()
        return user_data.get('login')
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to get user info. Check your token. {e}")
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
            if os.path.exists(REPO_CONFIG_FILE):
                os.remove(REPO_CONFIG_FILE)
            print("Success: Token has been removed.")
        except Exception as e:
            print(f"Error: Failed to remove token file: {e}")
    else:
        print("Error: Provided key does not match the stored token or no token is stored.")

def upload(args):
    """Uploads a file to GitHub."""
    global _current_repo
    if not _current_repo:
        print("Error: No repository selected. Use 'repo <reponame>' first.")
        return
    if not args:
        print("Error: 'upload' requires a filename.")
        return
    file_to_upload = args[0]
    if not file_to_upload.endswith('.cire'):
        print(f"Error: Invalid file extension. Only '.cire' files are supported.")
        return
    try:
        with open(file_to_upload, 'rb') as f:
            content = f.read()
            encoded_content = base64.b64encode(content).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: File '{file_to_upload}' not found.")
        return
    headers = _get_auth_headers()
    if not headers:
        return
    owner, repo = _current_repo.split('/')
    upload_url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/contents/{file_to_upload}"
    try:
        response = requests.get(upload_url, headers=headers)
        sha = None
        if response.status_code == 200:
            sha = response.json().get('sha')
        payload = {
            "message": f"Update {file_to_upload}",
            "content": encoded_content,
        }
        if sha:
            payload["sha"] = sha
        response = requests.put(upload_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        print(f"Success: File '{file_to_upload}' uploaded to '{_current_repo}'.")
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to upload file. {e}")

def download(args):
    """Downloads a file from GitHub."""
    global _current_repo
    if not _current_repo:
        print("Error: No repository selected. Use 'repo <reponame>' first.")
        return
    if not args:
        print("Error: 'download' requires a filename.")
        return
    file_to_download = args[0]
    owner, repo = _current_repo.split('/')
    download_url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/contents/{file_to_download}"
    headers = _get_auth_headers()
    if not headers:
        return
    try:
        response = requests.get(download_url, headers=headers)
        response.raise_for_status()
        content = response.json().get('content')
        if not content:
            print(f"Error: File '{file_to_download}' has no content.")
            return
        decoded_content = base64.b64decode(content)
        with open(file_to_download, 'wb') as f:
            f.write(decoded_content)
        print(f"Success: File '{file_to_download}' downloaded from '{_current_repo}'.")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"Error: File '{file_to_download}' not found in repository.")
        else:
            print(f"Error: Failed to download file. {e}")
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")

def repo(args):
    """Manages the current repository."""
    global _current_repo
    if not args:
        if _current_repo:
            print(f"Current repository: {_current_repo}")
        else:
            print("No repository selected. Use 'repo <reponame>' to select one.")
        return
    if args[0] == '-n' and len(args) > 1:
        repo_name = args[1]
        owner = _get_repo_owner()
        if not owner:
            return
        headers = _get_auth_headers()
        if not headers:
            return
        payload = {"name": repo_name, "private": False}
        print(f"Creating new repository '{repo_name}'...")
        try:
            response = requests.post(f"{GITHUB_API_URL}/user/repos", headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            print(f"Success: Repository '{repo_name}' created.")
            _current_repo = f"{owner}/{repo_name}"
            _save_repo(_current_repo)
            print(f"Now in repository: {_current_repo}")
        except requests.exceptions.RequestException as e:
            print(f"Error: Failed to create repository. {e}")
    else:
        repo_name = args[0]
        owner = _get_repo_owner()
        if owner:
            _current_repo = f"{owner}/{repo_name}"
            _save_repo(_current_repo)
            print(f"Now in repository: {_current_repo}")
        else:
            print("Error: Could not determine user owner to set repository.")

def rm(args):
    """Deletes files from the repository."""
    global _current_repo
    if not _current_repo:
        print("Error: No repository selected. Use 'repo <reponame>' first.")
        return
    if not args:
        print("Error: 'rm' requires arguments. Use '--one <file>' or '--all'.")
        return
    owner, repo = _current_repo.split('/')
    headers = _get_auth_headers()
    if not headers:
        return
    if args[0] == '--one' and len(args) > 1:
        file_to_delete = args[1]
        if not file_to_delete.endswith('.cire'):
            print(f"Error: Invalid file extension. Only '.cire' files can be deleted.")
            return
        check_url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/contents/{file_to_delete}"
        try:
            response = requests.get(check_url, headers=headers)
            response.raise_for_status()
            sha = response.json().get('sha')
            payload = {
                "message": f"Delete {file_to_delete}",
                "sha": sha
            }
            delete_url = check_url
            response = requests.delete(delete_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            print(f"Success: File '{file_to_delete}' deleted.")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"Error: File '{file_to_delete}' not found in repository.")
            else:
                print(f"Error: Failed to delete file. {e}")
        except Exception as e:
            print(f"Error: An unexpected error occurred: {e}")
    elif args[0] == '--all':
        list_url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/contents"
        try:
            response = requests.get(list_url, headers=headers)
            response.raise_for_status()
            files = response.json()
            for file_info in files:
                if file_info['name'].endswith('.cire'):
                    file_name = file_info['name']
                    sha = file_info['sha']
                    payload = {
                        "message": f"Delete {file_name}",
                        "sha": sha
                    }
                    delete_url = file_info['url']
                    response = requests.delete(delete_url, headers=headers, data=json.dumps(payload))
                    response.raise_for_status()
                    print(f"Success: File '{file_name}' deleted.")
            print("Success: All .cire files have been deleted.")
        except requests.exceptions.RequestException as e:
            print(f"Error: Failed to delete all files. {e}")
    else:
        print("Error: Invalid 'rm' command. Use '--one <file>' or '--all'.")

def mode():
    _load_repo()
    global _current_repo
    print("Welcome to Pico Shell. Use 'exit' to return to Cirebon.")
    print("*******************************************************")
    print("Pico                 Build 00/0                     1.0")
    while True:
        prompt_text = f"pico {_current_repo or '(none)'} >>> "
        try:
            pico_input = input(prompt_text)
            pico_parts = pico_input.split()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting Pico Shell...")
            break
        if not pico_parts:
            continue
        pico_command = pico_parts[0]
        pico_args = pico_parts[1:]
        if pico_command == "exit":
            print("Exiting Pico Shell...")
            break
        elif pico_command == "auth":
            auth(pico_args)
        elif pico_command == "logdown":
            logdown(pico_args)
        elif pico_command == "upload":
            upload(pico_args)
        elif pico_command == "download":
            download(pico_args)
        elif pico_command == "repo":
            repo(pico_args)
        elif pico_command == "rm":
            rm(pico_args)
        else:
            print(f"Error: Unknown pico command '{pico_command}'.")
