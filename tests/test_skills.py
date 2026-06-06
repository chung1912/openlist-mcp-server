"""Tests for the shared skills module (skills.py)."""

from openlist_mcp.skills import (
    ALWAYS_LOADED,
    SKILL_GROUP_META,
    SKILL_GROUP_TOOLS,
    SKILL_PRESETS,
    count_tools,
    group_count,
    resolve_skills,
)


class TestPresets:
    """Verify preset definitions produce expected tool counts."""

    def test_core_preset(self) -> None:
        groups = resolve_skills("core")
        assert groups == SKILL_PRESETS["core"]
        # core = auth + fs + transfer
        assert count_tools(groups) == group_count("auth") + group_count("fs") + group_count(
            "transfer"
        )

    def test_default_preset(self) -> None:
        groups = resolve_skills("default")
        assert groups == SKILL_PRESETS["default"]

    def test_all_preset(self) -> None:
        groups = resolve_skills("all")
        assert groups == SKILL_PRESETS["all"]
        # all should include every group except auth (which is always loaded)
        assert groups == {k for k in SKILL_GROUP_META if k != "auth"}

    def test_all_preset_has_all_tools(self) -> None:
        """all preset should cover every tool from every group."""
        groups = resolve_skills("all")
        expected_tools = sum(len(SKILL_GROUP_TOOLS[g]) for g in groups)
        actual_tools = count_tools(groups) - group_count("auth")  # subtract auth
        assert actual_tools == expected_tools


class TestResolveSkills:
    """Test the resolve_skills() function."""

    def test_custom_comma_separated(self) -> None:
        assert resolve_skills("fs,transfer,task") == {"fs", "transfer", "task"}

    def test_custom_with_spaces(self) -> None:
        assert resolve_skills("  fs ,  task  ") == {"fs", "task"}

    def test_custom_with_invalid_ignored(self) -> None:
        assert resolve_skills("fs,invalid,task") == {"fs", "task"}

    def test_empty_string(self) -> None:
        """Empty string should return empty set (no preset matched)."""
        assert resolve_skills("") == set()

    def test_case_insensitive(self) -> None:
        assert resolve_skills("CORE") == SKILL_PRESETS["core"]
        assert resolve_skills("Default") == SKILL_PRESETS["default"]
        assert resolve_skills("ALL") == SKILL_PRESETS["all"]

    def test_mixed_case_custom(self) -> None:
        assert resolve_skills("FS,Task") == {"fs", "task"}

    def test_unknown_preset_returns_empty(self) -> None:
        assert resolve_skills("unknown") == set()


class TestCountTools:
    """Test the count_tools() function."""

    def test_empty_set(self) -> None:
        """Empty set should return only auth count."""
        assert count_tools(set()) == group_count("auth")

    def test_count_with_invalid_group(self) -> None:
        """Invalid group names should be ignored."""
        cnt = count_tools({"fs", "invalid_group"})
        assert cnt == group_count("auth") + group_count("fs")

    def test_count_auth_not_double_counted(self) -> None:
        """auth should not be double-counted if explicitly included."""
        cnt = count_tools({"auth", "fs"})
        assert cnt == group_count("auth") + group_count("fs")


class TestGroupCount:
    """Test the group_count() function."""

    def test_known_group(self) -> None:
        assert group_count("fs") > 0
        assert group_count("auth") == 6

    def test_unknown_group(self) -> None:
        assert group_count("nonexistent") == 0


class TestMetaToolsSync:
    """Verify SKILL_GROUP_META and SKILL_GROUP_TOOLS stay in sync."""

    def test_all_meta_groups_have_tools(self) -> None:
        """Every group in META should have a tools list."""
        for name in SKILL_GROUP_META:
            assert name in SKILL_GROUP_TOOLS, f"{name} in META but missing from TOOLS"

    def test_all_tools_groups_have_meta(self) -> None:
        """Every group in TOOLS should have a META entry."""
        for name in SKILL_GROUP_TOOLS:
            assert name in SKILL_GROUP_META, f"{name} in TOOLS but missing from META"

    def test_always_loaded_is_valid(self) -> None:
        """ALWAYS_LOADED groups must exist in META."""
        for name in ALWAYS_LOADED:
            assert name in SKILL_GROUP_META, f"ALWAYS_LOADED '{name}' not in META"

    def test_preset_groups_are_valid(self) -> None:
        """All groups referenced in presets must exist in META."""
        for preset_name, groups in SKILL_PRESETS.items():
            for g in groups:
                assert g in SKILL_GROUP_META, (
                    f"Preset '{preset_name}' references '{g}' which is not in META"
                )


class TestGroupCountConsistency:
    """Verify group counts against actual tool lists."""

    def test_all_group_counts_match(self) -> None:
        """For every group, group_count() should equal len(SKILL_GROUP_TOOLS[name])."""
        for name in SKILL_GROUP_META:
            expected = len(SKILL_GROUP_TOOLS.get(name, []))
            actual = group_count(name)
            assert actual == expected, f"{name}: group_count({actual}) != len(tools)({expected})"
