# The Slasher 🔪

**The Slasher** is an unofficial fan-made Discord horror minigame bot. It randomly hunts server members, gives the victim a limited time to react, tracks survival statistics, generates VHS-style hunt cards, and can optionally use Google Gemini to write short lore-aware scenes for each horror encounter.

![The Slasher VHS hunt-card frame](assets/slasher_vhs_frame.png)

## Features

- **21 horror encounters** with different personalities, rarity, mechanics, and lore
- Interactive victim-only hunt choices
- Classic `RUN / HIDE / FIGHT` gameplay plus encounter-specific special choices
- Automatic random hunts with configurable timing and channel
- Rarity weighting and occasional fake-out appearances
- Persistent player stats, survival streaks, leaderboards, and encounter stats
- Dynamically generated VHS-style hunt cards
- Optional Gemini scene writing backed by curated lore profiles
- Built-in dialogue fallback if Gemini is disabled, unavailable, or errors
- `Slasher Protected` opt-out role
- Private `/slasher setup` admin dashboard
- Local SQLite persistence
- Designed to run locally or 24/7 on a small Linux VM

## Current roster

### Original roster

- Michael Myers
- Jason Voorhees
- Ghostface
- Leatherface
- Chucky
- Captain Spaulding
- Art the Clown
- Freddy Krueger
- Candyman
- Pinhead

### Expanded encounters

- Pumpkinhead
- Jack Torrance
- Pennywise
- Norman Bates
- Xenomorph
- Killer Klowns
- Deadites
- Jigsaw
- Leprechaun
- The Thing
- Count Orlok / Nosferatu

## How a hunt works

The bot selects an eligible member and an encounter. The victim gets about **30 seconds** to react.

Python controls the actual game:

- victim selection
- encounter selection and rarity
- action modifiers
- kill/survival probability
- stats and streaks
- automatic-hunt timing
- fake-outs

Gemini, when enabled, **only writes short scene flavor** based on the selected encounter's curated lore profile.

Most encounters use:

- 🏃 **RUN**
- 🫥 **HIDE**
- 👊 **FIGHT**

Several encounters use custom choices:

| Encounter | Special choices |
| --- | --- |
| Freddy Krueger | `WAKE UP / RUN / FIGHT` |
| Candyman | `STAY SILENT / RUN / SAY HIS NAME` |
| Pinhead | `SOLVE THE BOX / RUN / BEG` |
| Pennywise | `FACE YOUR FEAR / RUN / LOOK AWAY` |
| Xenomorph | `STAY QUIET / RUN / FIGHT` |
| Killer Klowns | `HIT THE NOSE / RUN / HIDE` |
| Deadites | `RECITE THE PASSAGE / RUN / FIGHT` |
| Jigsaw | `PLAY THE GAME / PANIC / CHEAT` |
| Leprechaun | `RETURN THE GOLD / RUN / FIGHT` |
| The Thing | `TEST THE BLOOD / RUN / TRUST SOMEONE` |
| Count Orlok | `FIND SUNLIGHT / RUN / HIDE` |

The VHS card mirrors the choices visually. The real Discord buttons underneath control gameplay.

## Requirements

- Python 3.11+
- A Discord application/bot token
- Discord **Server Members Intent** enabled
- Optional Google Gemini API key

## Quick installation

### 1. Download

Clone the repository:

```bash
git clone https://github.com/NukemLabs/SlasherBot.git
cd SlasherBot
```

Or use GitHub's **Code → Download ZIP** button and extract it.

### 2. Install dependencies

Windows:

```bat
py -m pip install -U -r requirements.txt
```

macOS/Linux:

```bash
python3 -m pip install -U -r requirements.txt
```

Windows users can also run `install.bat`.

### 3. Create `.env`

Copy `.env.example` to a new file named `.env`:

```env
DISCORD_TOKEN=your_real_token_here
DEV_GUILD_ID=
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.5-flash-lite
```

**Never commit `.env`, your Discord bot token, or your Gemini API key.**

`DEV_GUILD_ID` is optional. Setting it to a test server ID makes slash-command changes appear quickly while developing. Leave it blank for global command syncing.

### 4. Discord Developer Portal

For your Discord bot application:

1. Open the **Bot** section.
2. Enable **Server Members Intent**.
3. Create an OAuth2 invite with:
   - `bot`
   - `applications.commands`
4. Give The Slasher:
   - View Channels
   - Send Messages
   - Send Messages in Threads
   - Embed Links
   - Attach Files

**Administrator permission is not required.**

### 5. Start

Windows:

```bat
py bot.py
```

or run `start.bat`.

macOS/Linux:

```bash
python3 bot.py
```

Then have a server admin run:

```text
/slasher setup
```

## Server setup

`/slasher setup` opens a private admin dashboard for:

- automatic hunts
- hunt channel
- random hunt frequency
- Gemini writing

To prevent a member from being selected randomly, create a Discord role named exactly:

```text
Slasher Protected
```

Anyone with that role is excluded from automatic victim selection.

## Gemini is optional

The game does **not** require Gemini.

Without Gemini, The Slasher uses built-in writing and remains fully playable.

With Gemini enabled, the bot gives Gemini a curated lore profile for the selected encounter, the available actions, and encounter rarity. Gemini returns short scene-writing fields. Python still decides the gameplay result.

The bot uses a `{victim}` placeholder during generation and fills the Discord username locally afterward.

Useful commands:

```text
/slasher ai
/slasher aistatus
/slasher aitest
```

## Main commands

| Command | What it does |
| --- | --- |
| `/slasher setup` | Private admin setup dashboard |
| `/slasher roster` | Show the encounter roster |
| `/slasher status` | Check whether a hunt is active |
| `/slasher stats` | Player hunt statistics |
| `/slasher leaderboard` | Server survival leaderboard |
| `/slasher killerstats` | Encounter statistics |
| `/slasher hunt` | Admin random test hunt |
| `/slasher huntkiller` | Admin hunt with a chosen encounter |
| `/slasher auto` | Enable/disable automatic hunts |
| `/slasher channel` | Set automatic-hunt channel |
| `/slasher frequency` | Set automatic-hunt timing |
| `/slasher autosettings` | View automatic-hunt settings |
| `/slasher ai` | Enable/disable Gemini writing |
| `/slasher aistatus` | Check Gemini configuration |
| `/slasher aitest` | Generate a private AI preview |

## Persistent data

The bot stores server IDs, Discord user IDs, hunt statistics, streaks, encounter statistics, and guild configuration in:

```text
data/slasher.db
```

This database is ignored by Git and should **not** be uploaded publicly.

See [PRIVACY.md](PRIVACY.md).

## Run 24/7 for free

A small Linux VM is a good fit because The Slasher is a continuously running Discord process and uses a local SQLite database.

See **[HOSTING_GOOGLE_CLOUD.md](HOSTING_GOOGLE_CLOUD.md)** for a step-by-step Google Cloud Free Tier deployment guide.

## Updating a hosted copy

```bash
cd ~/SlasherBot
git pull
source .venv/bin/activate
pip install -U -r requirements.txt
sudo systemctl restart slasherbot
```

## Project structure

```text
SlasherBot/
├── assets/
│   └── slasher_vhs_frame.png
├── cogs/
│   └── slasher.py
├── data/
│   └── .gitkeep
├── game/
│   ├── actions.py
│   ├── auto_hunts.py
│   ├── card_renderer.py
│   ├── database.py
│   ├── gemini_writer.py
│   ├── hunt_manager.py
│   └── presentation.py
├── lore/
│   └── profiles.py
├── slashers/
│   └── ...
├── .env.example
├── .gitignore
├── bot.py
└── requirements.txt
```

## Disclaimer

The Slasher is an **unofficial fan-made project** for entertainment. It is not affiliated with, endorsed by, or sponsored by the owners of the horror franchises or characters referenced by the project.

Character names and related trademarks belong to their respective rights holders.

The MIT License applies to the original project code and original project assets included in this repository; it does not grant rights to third-party characters, names, or trademarks.

## License

Original project code and original included assets are released under the [MIT License](LICENSE).
