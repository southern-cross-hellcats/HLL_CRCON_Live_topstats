import importlib.util
import sys
import types
import unittest
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

    discord_module.SyncWebhook = FakeSyncWebhook
    discord_module.Embed = FakeEmbed
    sys.modules["discord"] = discord_module

    rcon_package = types.ModuleType("rcon")
    rcon_package.__path__ = []
    sys.modules["rcon"] = rcon_package

    rcon_rcon_module = types.ModuleType("rcon.rcon")
    rcon_rcon_module.Rcon = object
    rcon_rcon_module.StructuredLogLineWithMetaData = dict
    sys.modules["rcon.rcon"] = rcon_rcon_module

    user_config_package = types.ModuleType("rcon.user_config")
    user_config_package.__path__ = []
    sys.modules["rcon.user_config"] = user_config_package

    server_settings_module = types.ModuleType("rcon.user_config.rcon_server_settings")

    class FakeSettingsConfig:
        @staticmethod
        def load_from_db():
            return types.SimpleNamespace(server_url="https://example.com")

    server_settings_module.RconServerSettingsUserConfig = FakeSettingsConfig
    sys.modules["rcon.user_config.rcon_server_settings"] = server_settings_module

    utils_module = types.ModuleType("rcon.utils")
    utils_module.get_server_number = lambda: "1"
    sys.modules["rcon.utils"] = utils_module

    spec = importlib.util.spec_from_file_location("test_live_topstats_module", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


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
