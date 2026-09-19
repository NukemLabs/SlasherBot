# Publishing The Slasher to GitHub

Repository:

```text
NukemLabs/SlasherBot
```

## Browser upload method

1. Extract the GitHub-ready ZIP.
2. Open the extracted folder.
3. Go to the empty `NukemLabs/SlasherBot` repository.
4. Click **uploading an existing file** or **Add file → Upload files**.
5. Drag the **contents inside** the extracted folder into GitHub.
6. Confirm you see `.env.example`.
7. Confirm you do **NOT** see `.env` or `data/slasher.db`.
8. Commit with:

```text
Initial release of The Slasher v1.0.0
```

## Git command method

Open Command Prompt inside the extracted project folder:

```bat
git init
git add .
git commit -m "Initial release of The Slasher v1.0.0"
git branch -M main
git remote add origin https://github.com/NukemLabs/SlasherBot.git
git push -u origin main
```

If the remote already exists:

```bat
git remote set-url origin https://github.com/NukemLabs/SlasherBot.git
```

## Never upload

- `.env`
- Discord bot tokens
- Gemini API keys
- `data/slasher.db`
- virtual environments
- `__pycache__`

The included `.gitignore` blocks these.
