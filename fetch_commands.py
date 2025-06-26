#!/usr/bin/env python3
"""
Script to fetch slash commands from awesome-claude-code README and set them up locally
"""
import os
import re
import requests
from pathlib import Path
import time

def extract_commands_from_readme():
    """Extract all slash command entries from README.md"""
    with open('README.md', 'r') as f:
        content = f.read()
    
    # Pattern to match slash command entries
    pattern = r'\[`(/[^`]+)`\]\(([^)]+)\)'
    matches = re.findall(pattern, content)
    
    commands = []
    for match in matches:
        command_name = match[0]
        url = match[1]
        if command_name.startswith('/'):
            commands.append((command_name, url))
    
    return commands

def convert_to_raw_url(github_url):
    """Convert GitHub URL to raw content URL"""
    # Handle different GitHub URL patterns
    if 'github.com' in github_url and '/blob/' in github_url:
        parts = github_url.split('github.com/')[-1].split('/blob/')
        repo_part = parts[0]
        file_part = parts[1]
        return f"https://raw.githubusercontent.com/{repo_part}/{file_part}"
    elif 'gist.github.com' in github_url:
        # Handle gist URLs
        if '#file-' in github_url:
            base_url = github_url.split('#')[0]
            file_name = github_url.split('#file-')[-1].replace('-', '.')
            gist_id = base_url.split('/')[-1]
            user = base_url.split('/')[-2]
            return f"https://gist.githubusercontent.com/{user}/{gist_id}/raw/{file_name}"
    return github_url

def fetch_command_content(url):
    """Fetch content from a URL"""
    try:
        raw_url = convert_to_raw_url(url)
        response = requests.get(raw_url, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to fetch {raw_url}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def save_command(command_name, content, output_dir):
    """Save command content to file"""
    # Clean command name for filename
    filename = command_name.strip('/').replace('/', '_') + '.md'
    filepath = output_dir / filename
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"Saved: {command_name} -> {filepath}")

def main():
    # Create output directory
    output_dir = Path.home() / '.claude' / 'commands'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract commands from README
    print("Extracting commands from README.md...")
    commands = extract_commands_from_readme()
    print(f"Found {len(commands)} slash commands")
    
    # Fetch and save each command
    success_count = 0
    for i, (command_name, url) in enumerate(commands):
        print(f"\n[{i+1}/{len(commands)}] Processing {command_name}")
        print(f"  URL: {url}")
        
        content = fetch_command_content(url)
        if content:
            save_command(command_name, content, output_dir)
            success_count += 1
        
        # Be polite to GitHub
        time.sleep(0.5)
    
    print(f"\n✅ Successfully fetched and saved {success_count}/{len(commands)} commands")
    print(f"📁 Commands saved to: {output_dir}")

if __name__ == "__main__":
    main()