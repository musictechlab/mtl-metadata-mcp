# mtl-metadata-mcp

MCP server for reading and embedding metadata in audio files (MP3, FLAC, OGG).

## Tools

| Tool | Description |
|------|-------------|
| `metadata_read` | Read metadata tags and file info from an audio file |
| `metadata_write` | Embed metadata (title, artist, album, date, genre, ISRC) into an audio file |
| `metadata_clear` | Remove all metadata tags from an audio file |
| `metadata_scan` | Scan a directory for audio files and report metadata status |

## Setup

```bash
cd mtl-metadata-mcp
poetry install
```

## Claude Code configuration

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "mtl-metadata": {
      "command": "/Users/msmenzyk/work/musictechlab/mtl-metadata-mcp/.venv/bin/python",
      "args": ["-m", "mtl_metadata_mcp"]
    }
  }
}
```
