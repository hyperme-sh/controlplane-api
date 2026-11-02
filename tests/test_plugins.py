import pytest

def test_plugin_registration_does_not_alias_or_overwrite_declarations():
    from controlplane_api.operator.plugins import PLUGINS, known_action, plugin_by_id, register_plugin
    before = list(PLUGINS)
    declaration = {"id": "example.local", "title": "Example", "kind": "builtin", "permission": "operator:support",
                   "reads": ["/example"], "actions": ["inspect"]}
    try:
        register_plugin(declaration)
        declaration["actions"].append("mutate")
        assert known_action("example.local", "inspect")
        assert not known_action("example.local", "mutate")
        row = plugin_by_id("example.local")
        row["actions"].append("overwrite")
        assert not known_action("example.local", "overwrite")
        with pytest.raises(ValueError, match="already registered"):
            register_plugin(declaration)
        with pytest.raises(ValueError, match="required"):
            register_plugin({"id": "invalid"})
    finally:
        PLUGINS[:] = before
