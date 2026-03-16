"""Tests for audio metadata read/write operations."""

from pathlib import Path

import pytest

from mtl_metadata_mcp.metadata import (
    FIELD_MAP,
    SUPPORTED_EXTENSIONS,
    _validate_path,
    read_metadata,
    write_metadata,
)


def _make_mp3(tmp_path: Path, name: str = "test.mp3") -> Path:
    """Create a minimal valid MP3 file (silence frames)."""
    frame_header = bytes([0xFF, 0xFB, 0x90, 0x00])
    frame_data = b"\x00" * 413
    path = tmp_path / name
    path.write_bytes((frame_header + frame_data) * 10)
    return path


class TestValidatePath:
    def test_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            _validate_path(str(tmp_path / "nonexistent.mp3"))

    def test_unsupported_format(self, tmp_path):
        path = tmp_path / "test.wav"
        path.write_bytes(b"\x00" * 100)
        with pytest.raises(ValueError, match="Unsupported format"):
            _validate_path(str(path))

    def test_valid_mp3(self, tmp_path):
        path = _make_mp3(tmp_path)
        result = _validate_path(str(path))
        assert result == path.resolve()


class TestReadMetadata:
    def test_read_empty_mp3(self, tmp_path):
        path = _make_mp3(tmp_path)
        result = read_metadata(str(path))

        assert result["format"] == "mp3"
        assert result["file"] == str(path.resolve())
        assert result["duration_seconds"] is not None
        assert result["bitrate_kbps"] == 128
        assert result["sample_rate_hz"] == 44100
        assert result["channels"] == 2
        assert result["metadata"] == {}

    def test_read_after_write(self, tmp_path):
        path = _make_mp3(tmp_path)
        write_metadata(str(path), title="Test Song", artist="Test Artist")
        result = read_metadata(str(path))

        assert result["metadata"]["title"] == "Test Song"
        assert result["metadata"]["artist"] == "Test Artist"

    def test_read_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            read_metadata("/tmp/nonexistent_audio_file.mp3")


class TestWriteMetadata:
    def test_write_single_field(self, tmp_path):
        path = _make_mp3(tmp_path)
        result = write_metadata(str(path), title="My Track")

        assert result["metadata"]["title"] == "My Track"

    def test_write_all_fields(self, tmp_path):
        path = _make_mp3(tmp_path)
        result = write_metadata(
            str(path),
            title="Back in Black",
            artist="AC/DC",
            album="Back in Black",
            date="1980",
            genre="Classic Rock",
            isrc="AUAP07900028",
        )

        meta = result["metadata"]
        assert meta["title"] == "Back in Black"
        assert meta["artist"] == "AC/DC"
        assert meta["album"] == "Back in Black"
        assert meta["date"] == "1980"
        assert meta["genre"] == "Classic Rock"
        assert meta["isrc"] == "AUAP07900028"

    def test_write_preserves_existing(self, tmp_path):
        path = _make_mp3(tmp_path)
        write_metadata(str(path), title="Original", artist="Artist1")
        result = write_metadata(str(path), genre="Rock")

        meta = result["metadata"]
        assert meta["title"] == "Original"
        assert meta["artist"] == "Artist1"
        assert meta["genre"] == "Rock"

    def test_write_no_valid_fields(self, tmp_path):
        path = _make_mp3(tmp_path)
        with pytest.raises(ValueError, match="No valid fields"):
            write_metadata(str(path), invalid_field="value")

    def test_write_skips_none_values(self, tmp_path):
        path = _make_mp3(tmp_path)
        result = write_metadata(str(path), title="Set", artist=None)

        assert result["metadata"]["title"] == "Set"
        assert "artist" not in result["metadata"]

    def test_write_overwrites_existing(self, tmp_path):
        path = _make_mp3(tmp_path)
        write_metadata(str(path), title="Old Title")
        result = write_metadata(str(path), title="New Title")

        assert result["metadata"]["title"] == "New Title"


class TestConstants:
    def test_field_map_keys(self):
        assert set(FIELD_MAP.keys()) == {
            "title",
            "artist",
            "album",
            "date",
            "genre",
            "isrc",
        }

    def test_supported_extensions(self):
        assert SUPPORTED_EXTENSIONS == {".mp3", ".flac", ".ogg"}
