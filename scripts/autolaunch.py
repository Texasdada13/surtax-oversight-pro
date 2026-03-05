#!/usr/bin/env python
"""
Auto-launch script for Surtax Oversight Pro.
Generates a random session codename and port, starts the server, and opens the browser.
Designed to be triggered by VS Code on folder open.
"""

import os
import sys
import random
import socket
import time
import webbrowser
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- Random codename generator ---
ADJECTIVES = [
    'alpha', 'blazing', 'cosmic', 'diamond', 'emerald', 'falcon', 'golden',
    'horizon', 'iron', 'jade', 'krypton', 'lunar', 'mystic', 'nova',
    'obsidian', 'phantom', 'quantum', 'raven', 'shadow', 'titan',
    'ultra', 'vortex', 'wildfire', 'xenon', 'zenith', 'arctic',
    'bolt', 'cipher', 'delta', 'echo', 'forge', 'granite', 'hydra',
    'ignite', 'jetstream', 'kinetic', 'lightspeed', 'magnet', 'nitro',
    'omega', 'prism', 'quasar', 'reactor', 'sentinel', 'thunder',
]

NOUNS = [
    'station', 'nexus', 'vault', 'citadel', 'outpost', 'beacon',
    'fortress', 'matrix', 'spire', 'arsenal', 'bunker', 'core',
    'dome', 'engine', 'gateway', 'hub', 'lab', 'mainframe',
    'node', 'ops', 'portal', 'reactor', 'sector', 'terminal',
    'tower', 'base', 'chamber', 'deck', 'forge', 'grid',
    'hangar', 'interface', 'junction', 'keep', 'ledger',
]


def generate_codename():
    """Generate a random two-word codename like 'quantum-nexus'."""
    return f"{random.choice(ADJECTIVES)}-{random.choice(NOUNS)}"


def find_open_port(start=7000, end=9999):
    """Find a random open port in the given range."""
    attempts = 0
    while attempts < 50:
        port = random.randint(start, end)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                attempts += 1
    return 5847  # fallback


def open_browser_delayed(url, delay=2.0):
    """Open browser after a short delay to let the server start."""
    time.sleep(delay)
    webbrowser.open(url)


def main():
    codename = generate_codename()
    port = find_open_port()
    county = os.environ.get('SURTAX_COUNTY', 'marion')
    url = f"http://127.0.0.1:{port}"

    # Write session info to a temp file for reference
    session_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.session')
    with open(session_file, 'w') as f:
        f.write(f"codename={codename}\n")
        f.write(f"port={port}\n")
        f.write(f"url={url}\n")
        f.write(f"county={county}\n")

    from app import create_app
    app = create_app(county=county)

    # Launch browser in background thread
    threading.Thread(target=open_browser_delayed, args=(url,), daemon=True).start()

    print()
    print("\033[36m" + "=" * 60 + "\033[0m")
    print(f"\033[1;36m  SURTAX OVERSIGHT PRO\033[0m")
    print(f"\033[36m  Session:  \033[1;33m{codename}\033[0m")
    print(f"\033[36m  County:   \033[0m{county.title()}")
    print(f"\033[36m  URL:      \033[1;32m{url}\033[0m")
    print("\033[36m" + "=" * 60 + "\033[0m")
    print(f"\033[90m  Browser will open automatically...\033[0m")
    print()

    app.run(
        host='127.0.0.1',
        port=port,
        debug=True,
    )


if __name__ == '__main__':
    main()
