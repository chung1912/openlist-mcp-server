# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Added MAINTAINERS.md for project maintenance documentation
- Added CONTRIBUTING.md for contributor guidelines
- Added CHANGELOG.md for version history tracking
- Added GitHub Actions CI/CD workflows
- Added unit tests for config and client modules
- Added GitHub issue and PR templates

## [0.2.2] - 2024

### Fixed
- Fixed version strings to match tag v0.2.2

## [0.2.1] - 2024

### Added
- Added .env file support (via python-dotenv)
- Added friendly installation message when environment variables not set
- Added troubleshooting section to README
- Added uninstall instructions
- Added security notes for configuration files
- Added venv/virtualenv setup instructions

### Fixed
- Fixed upload functionality

### Changed
- Revamped installation documentation
- Added detailed configuration paths for Claude Desktop

## [0.2.0] - 2024

### Added
- Added security fixes
- Added bug patches

## [0.1.0] - 2024

### Added
- Initial release of OpenList MCP Server
- File system tools: list_files, get_file_info, search_files, create_folder, rename, copy, move, remove
- Transfer tools: get_download_url, upload_file
- Task management tools: list_tasks, delete_task, retry_task, cancel_task
- Share management tools: create_share, list_shares, cancel_share, delete_share
- Authentication tools: login, get_public_settings
- Auto JWT authentication with token refresh
- Integration test suite
- MIT License
- README with Chinese and English versions
- QQ community and sponsor QR codes

[Unreleased]: https://github.com/hbestm/openlist-mcp-server/compare/v0.2.2...HEAD
[0.2.2]: https://github.com/hbestm/openlist-mcp-server/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/hbestm/openlist-mcp-server/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/hbestm/openlist-mcp-server/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/hbestm/openlist-mcp-server/releases/tag/v0.1.0
