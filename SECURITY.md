# Security

## Secrets

Never commit:

- `.env`
- Discord bot tokens
- Gemini API keys
- private credentials

If a secret is accidentally committed, assume it is compromised and rotate it immediately.

## Discord token

Regenerate a leaked Discord bot token in the Discord Developer Portal.

## Gemini key

Revoke or rotate a leaked Gemini API key in the service where it was created.

## Database

`data/slasher.db` contains Discord IDs and gameplay statistics and should not be committed publicly.

## Sharing logs

Remove or redact tokens, API keys, user IDs, and other sensitive information before posting debugging output.
