"""MCP server exposing audio metadata tools for Claude Code."""

import json
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .metadata import FIELD_MAP, SUPPORTED_EXTENSIONS, read_metadata, write_metadata

mcp = FastMCP(
    "mtl-metadata",
    instructions=(
        "Audio metadata embedding service — read and write metadata tags "
        "(title, artist, album, date, genre, ISRC) in MP3, FLAC, and OGG files."
    ),
)


@mcp.tool()
def metadata_read(file_path: str) -> str:
    """Read metadata from an audio file.

    Returns current metadata tags (title, artist, album, date, genre, ISRC)
    plus file info (format, duration, bitrate, sample rate, channels).

    Supported formats: MP3, FLAC, OGG.

    Args:
        file_path: Absolute path to the audio file.
    """
    try:
        result = read_metadata(file_path)
        return json.dumps(result, indent=2, ensure_ascii=False)
    except (FileNotFoundError, ValueError) as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def metadata_write(
    file_path: str,
    title: str | None = None,
    artist: str | None = None,
    album: str | None = None,
    date: str | None = None,
    genre: str | None = None,
    isrc: str | None = None,
) -> str:
    """Embed metadata into an audio file.

    Only provided fields are updated — others remain unchanged.
    After writing, returns the updated metadata.

    Supported formats: MP3, FLAC, OGG.

    Args:
        file_path: Absolute path to the audio file.
        title: Track title (e.g. "Back in Black").
        artist: Artist name (e.g. "AC/DC").
        album: Album name (e.g. "Back in Black").
        date: Release year or date (e.g. "1980").
        genre: Genre (e.g. "Classic Rock").
        isrc: International Standard Recording Code (e.g. "US-S1Z-99-00001").
    """
    try:
        result = write_metadata(
            file_path,
            title=title,
            artist=artist,
            album=album,
            date=date,
            genre=genre,
            isrc=isrc,
        )
        return json.dumps(result, indent=2, ensure_ascii=False)
    except (FileNotFoundError, ValueError, PermissionError) as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def metadata_clear(file_path: str) -> str:
    """Remove all metadata tags from an audio file.

    This strips all ID3/Vorbis tags. The audio data is preserved.

    Supported formats: MP3, FLAC, OGG.

    Args:
        file_path: Absolute path to the audio file.
    """
    import mutagen

    try:
        path = Path(file_path).expanduser().resolve()
        if not path.exists():
            return json.dumps({"error": f"File not found: {path}"})
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return json.dumps(
                {"error": f"Unsupported format: {path.suffix}. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"}
            )

        audio = mutagen.File(str(path))
        if audio is None:
            return json.dumps({"error": f"Could not parse: {path}"})

        audio.delete()
        return json.dumps({"status": "ok", "message": f"All metadata cleared from {path.name}"})
    except (FileNotFoundError, ValueError, PermissionError) as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def metadata_scan(directory: str, recursive: bool = True) -> str:
    """Scan a directory for audio files and report their metadata status.

    Useful for finding files missing metadata or auditing a music library.

    Args:
        directory: Absolute path to the directory to scan.
        recursive: Whether to search subdirectories (default: true).
    """
    try:
        dir_path = Path(directory).expanduser().resolve()
        if not dir_path.is_dir():
            return json.dumps({"error": f"Not a directory: {dir_path}"})

        pattern = "**/*" if recursive else "*"
        files = []

        for ext in SUPPORTED_EXTENSIONS:
            for p in dir_path.glob(f"{pattern}{ext}"):
                try:
                    info = read_metadata(str(p))
                    meta = info.get("metadata", {})
                    missing = [f for f in FIELD_MAP if f not in meta]
                    files.append({
                        "file": str(p),
                        "format": info["format"],
                        "has_metadata": bool(meta),
                        "fields_present": list(meta.keys()),
                        "fields_missing": missing,
                    })
                except (ValueError, FileNotFoundError) as e:
                    files.append({"file": str(p), "error": str(e)})

        return json.dumps(
            {"directory": str(dir_path), "total_files": len(files), "files": files},
            indent=2,
            ensure_ascii=False,
        )
    except (FileNotFoundError, ValueError, PermissionError) as e:
        return json.dumps({"error": str(e)})
