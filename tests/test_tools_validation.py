"""Tests for tool input validation helpers."""

import pytest

from openlist_mcp.tools import normalize_names, validate_name, validate_pagination, validate_path


class TestValidatePath:
    def test_accepts_openlist_paths(self) -> None:
        for path in ["/", "/downloads", "/foo/bar", "relative/path", "backup..2024.tar.gz"]:
            validate_path(path)

    def test_rejects_unsafe_path_components(self) -> None:
        for path in ["", "/foo/../bar", "/foo/./bar", "/foo//bar", "/..", "../foo"]:
            with pytest.raises(ValueError):
                validate_path(path)


class TestValidateName:
    def test_accepts_filename_only_values(self) -> None:
        for name in ["file.txt", "backup..2024.tar.gz", "..hidden_file"]:
            validate_name(name)

    def test_rejects_paths_and_special_names(self) -> None:
        for name in ["", ".", "..", "dir/file.txt", r"dir\file.txt"]:
            with pytest.raises(ValueError):
                validate_name(name)

    def test_normalize_names_validates_each_item(self) -> None:
        assert normalize_names("a.txt, b.txt") == ["a.txt", "b.txt"]
        with pytest.raises(ValueError):
            normalize_names(["a.txt", "../b.txt"])


class TestValidatePagination:
    def test_accepts_valid_pagination(self) -> None:
        validate_pagination(1, 200)

    def test_rejects_invalid_pagination(self) -> None:
        for page, per_page in [(0, 50), (1, 0), (1, 201)]:
            with pytest.raises(ValueError):
                validate_pagination(page, per_page)
