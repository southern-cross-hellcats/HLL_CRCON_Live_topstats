# HLL_CRCON_Live_topstats

A plugin for Hell Let Loose (HLL) CRCON (see : https://github.com/MarechJ/hll_rcon_tool)
that displays and rewards top players, based on their scores.

![375489308-67943815-da9c-41ff-988c-eaaa2e0e64c2](https://github.com/user-attachments/assets/e44d0f07-23a8-4f62-87c4-742803c8be06)

## Features
- Enable/disable the script on the different servers managed in CRCON.
- Message can be called anytime with `!top` chat command (configurable).
- Message will be displayed to all players at game's end.
- Choose to give VIPs at game's end (you can define the number of top players that will receive one, and it's duration).
- Send the report in a Discord channel.
- Available in english, french, german, brazilian portuguese, polish and spanish.

## Observed scores

- (top players will earn a VIP at game's end)
    - commanders
        - combat + (support * bonus)
    - infantry players
        - offense + (defense * bonus)
        - combat + (support * bonus)
- (for info only - no VIPs given)
    - infantry players
        - kills / deaths
        - kills / minute
    - infantry squads
        - offense + (defense * bonus)
        - combat + (support * bonus)
    - armor squads
        - offense + (defense * bonus)
        - combat + (support * bonus)

A multiplier bonus can be given to defense and support scores, if you want to reward teamplay more than individual skills.  
Doing so will ensure the teamplayers will enter the server more often than CODdies.

Tankers don't get any VIP, as they usually have a huge combat score and would easily get a VIP on each game.

## Install

> [!NOTE]
> The shell commands given below assume your CRCON is installed in `/root/hll_rcon_tool`.  

- Log into your CRCON host machine using SSH and enter these commands (one line at at time) :  

  First part  
  If you already have installed any other "custom tools" from ElGuillermo, you can skip this part.  
  (though it's always a good idea to redownload the files, as they could have been updated)
  ```shell
  cd /root/hll_rcon_tool
  wget https://raw.githubusercontent.com/ElGuillermo/HLL_CRCON_restart/refs/heads/main/restart.sh
  mkdir custom_tools
  ```
  Second part
  ```shell
  cd /root/hll_rcon_tool/custom_tools
  wget https://raw.githubusercontent.com/ElGuillermo/HLL_CRCON_Live_topstats/refs/heads/main/hll_rcon_tool/custom_tools/live_topstats.py
  ```
- Edit `/root/hll_rcon_tool/rcon/hooks.py` and add these lines :
  - in the import part, on top of the file
    ```python
    import custom_tools.live_topstats as live_topstats
    ```
  - At the very end of the file
    ```python
    @on_chat
    def livetopstats_onchat(rcon: Rcon, struct_log: StructuredLogLineWithMetaData):
      live_topstats.stats_on_chat_command(rcon, struct_log)

    @on_match_end
    def livetopstats_onmatchend(rcon: Rcon, struct_log: StructuredLogLineWithMetaData):
      live_topstats.stats_on_match_end(rcon, struct_log)
    ```

## Config
- Configuration now supports environment variables, which fits naturally with CRCON's existing `.env` / `default.env` setup.
- A ready-to-copy sample file is included at `example.live_topstats.env`.
- Add the variables you want to override to your CRCON `.env` file, for example:
  ```env
  LIVE_TOPSTATS_LANG=0
  LIVE_TOPSTATS_ENABLE_ON_SERVERS=["1","2"]
  LIVE_TOPSTATS_CHAT_COMMAND=!top
  LIVE_TOPSTATS_TOPS_MATCHEND=3
  LIVE_TOPSTATS_VIP_WINNERS=1
  LIVE_TOPSTATS_VIP_HOURS=24
  LIVE_TOPSTATS_LOCAL_TIMEZONE=America/Argentina/Buenos_Aires
  LIVE_TOPSTATS_SERVER_CONFIG=[["https://discord.com/api/webhooks/REAL_SERVER_1",true],["https://discord.com/api/webhooks/REAL_SERVER_2",false]]
  ```
- Supported variables:
  - `LIVE_TOPSTATS_LANG`
  - `LIVE_TOPSTATS_ENABLE_ON_SERVERS` (`["1","2"]` JSON or `1,2` comma-separated)
  - `LIVE_TOPSTATS_OFFENSEDEFENSE_RATIO`
  - `LIVE_TOPSTATS_COMBATSUPPORT_RATIO`
  - `LIVE_TOPSTATS_CHAT_COMMAND`
  - `LIVE_TOPSTATS_TOPS_CHAT`
  - `LIVE_TOPSTATS_TOPS_CHAT_DETAIL_SQUADS`
  - `LIVE_TOPSTATS_TOPS_MATCHEND`
  - `LIVE_TOPSTATS_TOPS_MATCHEND_DETAIL_SQUADS`
  - `LIVE_TOPSTATS_VIP_WINNERS`
  - `LIVE_TOPSTATS_VIP_COMMANDER_MIN_PLAYTIME_MINS`
  - `LIVE_TOPSTATS_VIP_COMMANDER_MIN_SUPPORT_SCORE`
  - `LIVE_TOPSTATS_SEED_LIMIT`
  - `LIVE_TOPSTATS_VIP_HOURS`
  - `LIVE_TOPSTATS_SCORE_PER_MINUTE`
  - `LIVE_TOPSTATS_LOCAL_TIMEZONE`
  - `LIVE_TOPSTATS_SERVER_CONFIG` (JSON list of `[webhook_url, enabled]` pairs)
  - `LIVE_TOPSTATS_DISCORD_EMBED_AUTHOR_ICON_URL`
  - `LIVE_TOPSTATS_BOT_NAME`
- If an environment variable is not set, the plugin falls back to the current built-in default.
- You can still edit `/root/hll_rcon_tool/custom_tools/live_topstats.py`, but `.env` overrides are now the preferred way to configure the plugin.
- Restart CRCON :
  ```shell
  cd /root/hll_rcon_tool
  sh ./restart.sh
  ```

## Limitations
⚠️ Any change to these files requires a CRCON rebuild and restart (using the `restart.sh` script) to be taken in account :
- `/root/hll_rcon_tool/custom_tools/live_topstats.py`
- `/root/hll_rcon_tool/rcon/hooks.py`

⚠️ This plugin requires a modification of the `/root/hll_rcon_tool/rcon/hooks.py` file, which originates from the official CRCON depot.  
If any CRCON upgrade implies updating this file, the usual upgrade procedure, as given in official CRCON instructions, will **FAIL**.  
To successfully upgrade your CRCON, you'll have to revert the changes back, then reinstall this plugin.  
To revert to the original file :  
```shell
cd /root/hll_rcon_tool
git restore rcon/hooks.py
```
