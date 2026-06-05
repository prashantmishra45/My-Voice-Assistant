"""Windows application launcher."""

from __future__ import annotations

import os


class ApplicationLauncher:
    """Launch common Windows applications."""

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

    def open_application(self, name: str) -> str:
        """
        Open a supported Windows application.

        Args:
            name: Application name

        Returns:
            Status message
        """

        app = self.APPS.get(name.lower().strip())

        if not app:
            raise ValueError(
                f"Unsupported application: {name}. "
                f"Supported applications: {', '.join(self.APPS.keys())}"
            )

        os.system(f"start {app}")

        return f"Opened {name}"