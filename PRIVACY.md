# Privacy

The Slasher is a self-hosted Discord bot.

## Local data

The bot stores the following in its local SQLite database:

- Discord server IDs
- Discord user IDs
- hunt counts
- survival/death counts
- current and best survival streaks
- per-encounter statistics
- automatic-hunt configuration
- configured hunt-channel IDs
- Gemini enabled/disabled setting

The database is:

```text
data/slasher.db
```

It is excluded by `.gitignore`.

## Gemini

Gemini integration is optional.

When enabled, Gemini generates short horror-scene text from curated encounter lore, action choices, and rarity. The writer uses a `{victim}` placeholder during generation; the Discord username is inserted locally afterward.

The game engine—not Gemini—controls victim selection, probabilities, outcomes, timing, and statistics.

## Self-hosting

Anyone running a copy of The Slasher is responsible for the data stored by their own installation and for the policies of third-party services they configure.
