# PalBot

A quick Discord Bot for Palworld server maintenance

## What is this?

This discord bot allows simple functions like rebooting a target Palworld server, saving, and outputting the current memory.

## Usage

Currently, there are **FOUR** commands.

- `!memory` - Runs `free -ht` and returns the output
- `!save` - Runs the RCON save command
- `!upgrade` - Runs the steamapp upgrade command for the Palworld Server
- `!restart` - Will save and then restart the Palworld server. Prompts the user and times-out if they do not respond appropriately.

## Runtime - Ubuntu 22.04

Download the executable to your users home directory, in my case, `dan`.

```bash
LATEST_TAG="$(curl -s https://api.github.com/repos/danmanners/palworld-discord/tags | jq -r '.[0].name')"
wget -q https://github.com/danmanners/palworld-discord/releases/download/${LATEST_TAG}/bot -O ~/bot
chmod +x bot
```

Next, create your `.env` file in your users home directory.

> [!INFO]
> Check the [`examples/.env`](examples/.env) file for what information needs to be filled in.

Finally, create your `systemd` service.

```ini
# /lib/systemd/system/discord-bot.service
[Unit]
Description=Discord Bot for Palworld Server
After=network.target

[Service]
WorkingDirectory=/home/dan/
ExecStart=/home/dan/bot
Type=simple
User=dan
Group=dan
Restart=on-failure

[Install]
WantedBy=default.target
RequiredBy=network.target
```

Once that's loaded in, reload and enable the service.

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now discord-bot
```

Now you can test everything and validate!

## Local Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
python bot.py
```
