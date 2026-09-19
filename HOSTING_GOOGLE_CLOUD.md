# Run The Slasher 24/7 on Google Cloud

This setup keeps The Slasher online even when your own PC is turned off.

Google Cloud currently offers eligible Free Tier Compute Engine usage for an `e2-micro` VM in specific US regions. Free Tier rules can change, so verify Google's current limits before creating the VM.

## 1. Create the VM

In Google Cloud Console:

1. Create or select a project.
2. Make sure billing is enabled.
3. Open **Compute Engine → VM instances**.
4. Click **Create instance**.
5. Name it:

```text
slasher-bot
```

6. Choose one of the eligible Free Tier regions:
   - `us-east1`
   - `us-central1`
   - `us-west1`
7. Machine family: **E2**
8. Machine type:

```text
e2-micro
```

9. Boot disk:
   - Ubuntu
   - Ubuntu 24.04 LTS
   - Standard persistent disk
   - 10–30 GB
10. Do not add a GPU.
11. The bot does not serve a website, so HTTP/HTTPS firewall access is not required.
12. Create the VM.

## 2. Open SSH

On the VM instances page, click **SSH** beside `slasher-bot`.

## 3. Install software

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip
```

## 4. Clone The Slasher

```bash
git clone https://github.com/NukemLabs/SlasherBot.git
cd SlasherBot
```

## 5. Create the Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 6. Create the private `.env`

```bash
cp .env.example .env
nano .env
```

Fill in your real values:

```env
DISCORD_TOKEN=YOUR_REAL_DISCORD_TOKEN
DEV_GUILD_ID=
GEMINI_API_KEY=YOUR_REAL_GEMINI_KEY
GEMINI_MODEL=gemini-3.5-flash-lite
```

Save in nano with `Ctrl+O`, Enter, then `Ctrl+X`.

Protect it:

```bash
chmod 600 .env
```

Never put your real `.env` on GitHub.

## 7. Test

```bash
source .venv/bin/activate
python bot.py
```

Confirm The Slasher comes online in Discord.

Stop the manual test:

```text
Ctrl+C
```

## 8. Make it run automatically

Find your Linux username:

```bash
whoami
```

Create the service:

```bash
sudo nano /etc/systemd/system/slasherbot.service
```

Paste this and replace `YOUR_USERNAME` everywhere:

```ini
[Unit]
Description=The Slasher Discord Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/SlasherBot
ExecStart=/home/YOUR_USERNAME/SlasherBot/.venv/bin/python /home/YOUR_USERNAME/SlasherBot/bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now slasherbot
```

Check it:

```bash
sudo systemctl status slasherbot
```

Press `q` to exit the status view.

## Live logs

```bash
sudo journalctl -u slasherbot -f
```

Use `Ctrl+C` to leave the logs.

## Restart

```bash
sudo systemctl restart slasherbot
```

## Update from GitHub later

```bash
cd ~/SlasherBot
git pull
source .venv/bin/activate
pip install -U -r requirements.txt
sudo systemctl restart slasherbot
```

## Statistics

The SQLite database remains on the VM's persistent boot disk at:

```text
~/SlasherBot/data/slasher.db
```

Normal bot restarts and VM reboots do not delete it.

Do not delete the VM/disk unless you have backed up this file.

## Simple database backup

```bash
cd ~/SlasherBot
cp data/slasher.db ~/slasher.db.backup
```
