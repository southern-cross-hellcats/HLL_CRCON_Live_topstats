import importlib.util
import os
import sys
import types
import unittest
from typing import Any, cast
from unittest import mock
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "hll_rcon_tool" / "custom_tools" / "live_topstats.py"


def load_live_topstats_module():
    discord_module = types.ModuleType("discord")

    class FakeSyncWebhook:
        @classmethod
        def from_url(cls, _url):
            return cls()

        def send(self, **_kwargs):
            return None

    class FakeEmbed:
        def __init__(self, **_kwargs):
            pass

        def set_author(self, **_kwargs):
            return None

    setattr(discord_module, "SyncWebhook", FakeSyncWebhook)
    setattr(discord_module, "Embed", FakeEmbed)
    sys.modules["discord"] = discord_module

    rcon_package = types.ModuleType("rcon")
    rcon_package.__path__ = []
    sys.modules["rcon"] = rcon_package

    rcon_rcon_module = types.ModuleType("rcon.rcon")
    setattr(rcon_rcon_module, "Rcon", object)
    setattr(rcon_rcon_module, "StructuredLogLineWithMetaData", dict)
    sys.modules["rcon.rcon"] = rcon_rcon_module

    user_config_package = types.ModuleType("rcon.user_config")
    user_config_package.__path__ = []
    sys.modules["rcon.user_config"] = user_config_package

    server_settings_module = types.ModuleType("rcon.user_config.rcon_server_settings")

    class FakeSettingsConfig:
        @staticmethod
        def load_from_db():
            return types.SimpleNamespace(server_url="https://example.com")

    setattr(server_settings_module, "RconServerSettingsUserConfig", FakeSettingsConfig)
    sys.modules["rcon.user_config.rcon_server_settings"] = server_settings_module

    utils_module = types.ModuleType("rcon.utils")
    setattr(utils_module, "get_server_number", lambda: "1")
    sys.modules["rcon.utils"] = utils_module

    spec = importlib.util.spec_from_file_location("test_live_topstats_module", MODULE_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return cast(Any, module)


class LiveTopStatsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.live_topstats = load_live_topstats_module()

    def test_normalized_ratio_treats_zero_as_unweighted(self):
        self.assertEqual(self.live_topstats.normalized_ratio(0), 1)
        self.assertEqual(self.live_topstats.normalized_ratio(-1.75), 1.75)

    def test_local_time_format_uses_current_language(self):
        original_lang = self.live_topstats.LANG
        self.live_topstats.LANG = 5
        try:
            self.assertEqual(
                self.live_topstats.get_local_time_format(),
                "%d/%m/%Y a las %Hh%M",
            )
        finally:
            self.live_topstats.LANG = original_lang

    def test_get_env_list_supports_json_and_csv(self):
        with mock.patch.dict(os.environ, {"LIVE_TOPSTATS_TEST_LIST": '["1", "2"]'}, clear=False):
            self.assertEqual(self.live_topstats.get_env_list("LIVE_TOPSTATS_TEST_LIST", ["9"]), ["1", "2"])

        with mock.patch.dict(os.environ, {"LIVE_TOPSTATS_TEST_LIST": "1, 2,3"}, clear=False):
            self.assertEqual(self.live_topstats.get_env_list("LIVE_TOPSTATS_TEST_LIST", ["9"]), ["1", "2", "3"])

    def test_get_env_server_config_falls_back_on_invalid_json(self):
        default = [["https://discord.com/api/webhooks/default", False]]
        with mock.patch.dict(os.environ, {"LIVE_TOPSTATS_SERVER_CONFIG": "not-json"}, clear=False):
            self.assertEqual(self.live_topstats.get_env_server_config(default), default)

    def test_get_env_server_config_parses_json(self):
        default = [["https://discord.com/api/webhooks/default", False]]
        value = '[["https://discord.com/api/webhooks/one", true], ["https://discord.com/api/webhooks/two", false]]'
        with mock.patch.dict(os.environ, {"LIVE_TOPSTATS_SERVER_CONFIG": value}, clear=False):
            self.assertEqual(
                self.live_topstats.get_env_server_config(default),
                [
                    ["https://discord.com/api/webhooks/one", True],
                    ["https://discord.com/api/webhooks/two", False],
                ],
            )

    def test_get_top_lists_members_for_current_squad_only(self):
        class FakeRcon:
            pass

        output = self.live_topstats.get_top(
            rcon=FakeRcon(),
            callmode="chat",
            calltype="squad",
            data_bucket=[
                {
                    "name": "Able",
                    "team": "allies",
                    "offense": "200",
                    "defense": "100",
                    "combat": "0",
                    "support": "0",
                }
            ],
            sortkey=self.live_topstats.real_offdef,
            first_data="name",
            second_data="offense",
            third_data="defense",
            fourth_data="",
            squadtype_allplayers=[
                {"name": "Alice", "team": "allies", "unit_name": "Able"},
                {"name": "Bob", "team": "allies", "unit_name": "Able"},
                {"name": "Eve", "team": "axis", "unit_name": "Baker"},
            ],
        )

        self.assertIn("■ Able (all): 200 ; 100", output)
        self.assertIn("Alice; Bob", output)
        self.assertNotIn("Eve", output)


if __name__ == "__main__":
    unittest.main()
