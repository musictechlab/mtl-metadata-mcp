"""Core metadata reading and writing logic using mutagen."""

from pathlib import Path
from typing import Any

import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.id3 import TALB, TDRC, TIT2, TPE1, TSRC, ID3NoHeaderError
from mutagen.oggvorbis import OggVorbis

# Mapping from our field names to EasyID3/Vorbis tag names
FIELD_MAP = {
    "title": "title",
    "artist": "artist",
    "album": "album",
    "date": "date",
    "genre": "genre",
    "isrc": "isrc",
}

# For raw ID3 frames (MP3 fallback when EasyID3 doesn't work)
ID3_FRAME_MAP = {
    "title": TIT2,
    "artist": TPE1,
    "album": TALB,
    "date": TDRC,
    "isrc": TSRC,
}

SUPPORTED_EXTENSIONS = {".mp3", ".flac", ".ogg"}


def _validate_path(file_path: str) -> Path:
    """Validate that the file exists and is a supported format."""
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported format: {path.suffix}. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )
    return path


def read_metadata(file_path: str) -> dict[str, Any]:
    """Read metadata from an audio file.

    Returns a dict with standard fields plus file info.
    """
    path = _validate_path(file_path)
    audio = mutagen.File(str(path), easy=True)

    if audio is None:
        raise ValueError(f"Could not parse audio file: {path}")

    result: dict[str, Any] = {
        "file": str(path),
        "format": path.suffix.lower().lstrip("."),
        "duration_seconds": round(audio.info.length, 2) if audio.info else None,
        "bitrate_kbps": (
            round(audio.info.bitrate / 1000)
            if hasattr(audio.info, "bitrate") and audio.info.bitrate
            else None
        ),
        "sample_rate_hz": getattr(audio.info, "sample_rate", None),
        "channels": getattr(audio.info, "channels", None),
    }

    metadata = {}
    for field, tag in FIELD_MAP.items():
        values = audio.get(tag)
        if values:
            metadata[field] = values[0] if len(values) == 1 else list(values)

    result["metadata"] = metadata
    return result


def write_metadata(file_path: str, **fields: str) -> dict[str, Any]:
    """Write metadata fields to an audio file.

    Accepts keyword arguments for: title, artist, album, date, genre, isrc.
    Only provided fields are updated; others remain unchanged.
    Returns the updated metadata.
    """
    path = _validate_path(file_path)

    # Filter to only valid fields that were provided
    updates = {k: v for k, v in fields.items() if k in FIELD_MAP and v is not None}
    if not updates:
        raise ValueError(
            f"No valid fields provided. Valid fields: {', '.join(FIELD_MAP.keys())}"
        )

    ext = path.suffix.lower()

    if ext == ".mp3":
        _write_mp3(path, updates)
    elif ext == ".flac":
        _write_flac(path, updates)
    elif ext == ".ogg":
        _write_ogg(path, updates)

    return read_metadata(file_path)


def _write_mp3(path: Path, updates: dict[str, str]) -> None:
    """Write metadata to MP3 using EasyID3."""
    try:
        audio = EasyID3(str(path))
    except ID3NoHeaderError:
        audio = EasyID3()
        audio.filename = str(path)
        audio.save(str(path))
        audio = EasyID3(str(path))

    for field, value in updates.items():
        tag = FIELD_MAP[field]
        audio[tag] = value

    audio.save()


def _write_flac(path: Path, updates: dict[str, str]) -> None:
    """Write metadata to FLAC using Vorbis comments."""
    audio = FLAC(str(path))

    for field, value in updates.items():
        tag = FIELD_MAP[field]
        audio[tag] = value

    audio.save()


def _write_ogg(path: Path, updates: dict[str, str]) -> None:
    """Write metadata to OGG Vorbis."""
    audio = OggVorbis(str(path))

    for field, value in updates.items():
        tag = FIELD_MAP[field]
        audio[tag] = value

    audio.save()
