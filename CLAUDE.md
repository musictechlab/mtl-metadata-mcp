# mtl-metadata-mcp

MCP server for reading and embedding metadata in audio files.

## Tech Stack

- **Language**: Python 3.10+
- **Package manager**: Poetry
- **Audio library**: mutagen
- **MCP framework**: FastMCP (mcp[cli])
- **Linter**: Ruff
- **Test framework**: pytest

## Commands

| Action | Command |
|--------|---------|
| Install | `poetry install` |
| Run server | `poetry run python -m mtl_metadata_mcp` |
| Test | `poetry run pytest` |
| Lint | `poetry run ruff check .` |
| Format | `poetry run ruff format .` |

## Architecture

- `src/mtl_metadata_mcp/server.py` — MCP tool definitions
- `src/mtl_metadata_mcp/metadata.py` — Core read/write logic using mutagen
- `src/mtl_metadata_mcp/__main__.py` — Entry point

## Supported Formats

- MP3 (ID3v2 via EasyID3)
- FLAC (Vorbis comments)
- OGG (Vorbis comments)
