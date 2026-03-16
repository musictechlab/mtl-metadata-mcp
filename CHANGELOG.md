# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `metadata_read` — read metadata tags and file info from audio files
- `metadata_write` — embed title, artist, album, date, genre, ISRC
- `metadata_clear` — remove all metadata tags
- `metadata_scan` — scan directories for audio files and report metadata status
- Support for MP3 (ID3v2), FLAC, and OGG (Vorbis comments)
