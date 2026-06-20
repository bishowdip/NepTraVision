"""The data pipeline: raw footage → release-ready, leakage-safe dataset.

Stages (each is a CLI subcommand under ``neptravision data …``):

    frame_extraction → deduplicate → select → (annotate, external) →
    validate → splits → convert → stats

Heavy third-party imports (cv2, imagehash, pandas) are done lazily *inside*
functions so that importing :mod:`neptravision.data` stays cheap and the pure
modules (e.g. :mod:`~neptravision.data.splits`) are testable without them.
"""
