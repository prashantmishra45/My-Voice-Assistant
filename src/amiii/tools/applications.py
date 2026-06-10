"""Windows application launcher."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Optional
import webbrowser
import urllib.parse


class ApplicationLauncher:
    """Launch Windows applications and folders."""

    APPS = {
        "chrome": "chrome",
        "google chrome": "chrome",
        "vscode": "code",
        "vs code": "code",
        "code": "code",
        "notepad": "notepad",
        "calculator": "calc",
        "calc": "calc",
        "downloads": "explorer shell:Downloads",
        "documents": "explorer shell:Personal",
        "desktop": "explorer shell:Desktop",
        "pictures": "explorer shell:Pictures",
    }

    def find_start_menu_shortcut(self, app_name: str) -> Optional[str]:
        """
        Search Windows Start Menu shortcuts for an application.
        """

        search_paths = [
            Path(r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs"),
            Path.home() / r"AppData\Roaming\Microsoft\Windows\Start Menu\Programs",
        ]

        target = app_name.lower().strip()

        for root in search_paths:
            if not root.exists():
                continue

            for shortcut in root.rglob("*.lnk"):
                if target in shortcut.stem.lower():
                    return str(shortcut)

        return None

    def open_dynamic_application(self, app_name: str) -> str:
        """
        Open any installed application discovered via Start Menu.
        """

        shortcut = self.find_start_menu_shortcut(app_name)

        if shortcut:
            subprocess.Popen(
                ["powershell", "-Command", f'Start-Process "{shortcut}"']
            )
            return f"Opening {app_name}"

        raise ValueError(
            f"I couldn't find '{app_name}' on this computer."
        )

    def open_application(self, name: str) -> str:
        """
        Open a Windows application or folder.
        """

        clean_name = name.lower().strip()

        # First try built-in shortcuts
        app = self.APPS.get(clean_name)

        if app:
            os.system(f"start {app}")
            return f"Opened {name}"

        # Then try dynamic discovery
        return self.open_dynamic_application(name)

    def google_search(self, query: str) -> str:
        """
        Search Google using the default browser.
        """
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.google.com/search?q={encoded_query}"
        webbrowser.open(url)
        return f"Searching Google for {query}"

    def open_website(self, target: str) -> str:
        """
        Open a specific website.
        """
        websites = {
            "youtube": "https://www.youtube.com",
            "github": "https://github.com",
            "linkedin": "https://www.linkedin.com",
            "gmail.com": "https://mail.google.com",
            "gmail": "https://mail.google.com"
        }
        
        clean_target = target.lower().strip()
        url = websites.get(clean_target)
        
        if url:
            webbrowser.open(url)
            return f"Opening {target}"
        
        # If not in our predefined list, just do a google search or open directly if it looks like a url
        if "." in clean_target:
            if not clean_target.startswith("http"):
                clean_target = f"https://{clean_target}"
            webbrowser.open(clean_target)
            return f"Opening {target}"

        return self.google_search(target)

    def play_media(self, query: str) -> str:
        """
        Search YouTube and open results.
        """
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={encoded_query}"
        webbrowser.open(url)
        return f"Playing {query} on YouTube"