"""Logging setup. One handler on the package-root logger; module loggers
propagate up to it — so each line is printed exactly once."""

import logging

_ROOT = "voice_assistant"
_configured = False


def get_logger(name: str) -> logging.Logger:
    global _configured
    if not _configured:
        root = logging.getLogger(_ROOT)
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", "%H:%M:%S")
        )
        root.addHandler(handler)
        root.setLevel(logging.INFO)
        root.propagate = False  # don't double-log via the root logger
        _configured = True
    return logging.getLogger(name)
