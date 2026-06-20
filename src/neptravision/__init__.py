"""NepTraVision — a Nepal-specific traffic computer-vision benchmark.

The public surface is intentionally small. Most work happens through the CLI
(`neptravision …`) or by importing the focused submodules:

    from neptravision.data import frame_extraction, deduplicate, splits
    from neptravision.config import load_settings

See ``docs/01_architecture.md`` for the module map.
"""

from __future__ import annotations

__version__ = "0.1.0"

__all__ = ["__version__"]
