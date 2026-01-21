"""Compatibility shim for legacy imports and CLI usage."""

from backend.app.services.reader3 import *  # noqa: F401,F403

if __name__ == "__main__":
    from backend.cli import main

    main()
