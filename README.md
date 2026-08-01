# FileStream Bot

A Telegram bot built with **Pyrofork (Pyrogram)** that turns any file sent to it (video, document, audio, voice, animation, photo) into an instant **streamable / downloadable web link** — no need to open Telegram to watch or download.

## ✨ Features

- 🔗 Generate direct stream & download links for any file sent to the bot (private chat or channel)
- ▶️ Built-in HTML video player (`play.html`) for streaming videos in the browser
- 📥 Dedicated download page (`dl.html`)
- 🗄️ MongoDB-backed file & user database
- 🚫 Force-subscribe support (require users to join a channel before use)
- 👑 Admin tools: ban/unban users or channels, broadcast messages, bot status, user list export
- ⚙️ Multi-client support for load balancing across bot tokens
- 🐳 Docker-ready, and pre-configured for one-click deploy on Render/Heroku

## 🧱 Project Structure

```
FileStream/
├── bot/
│   ├── plugins/
│   │   ├── start.py      # /start command, onboarding, force-sub check
│   │   ├── stream.py     # receives files, generates stream/download links
│   │   ├── admin.py      # admin commands (ban, broadcast, status, etc.)
│   │   └── callback.py   # inline button callback handling
│   └── clients.py        # multi-client initialization
├── server/
│   └── stream_routes.py  # aiohttp routes that actually stream/serve files
├── utils/
│   ├── database.py       # MongoDB (motor) access layer
│   ├── file_properties.py
│   ├── bot_utils.py
│   └── ...
├── template/
│   ├── play.html          # video player page
│   └── dl.html             # download page
├── config.py              # all environment variable configuration
└── __main__.py             # entrypoint (starts bot + web server)
```

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.11+
- A MongoDB database (e.g. free tier on [MongoDB Atlas](https://www.mongodb.com/atlas))
- A Telegram **API_ID** and **API_HASH** from [my.telegram.org](https://my.telegram.org)
- A **Bot Token** from [@BotFather](https://t.me/BotFather)
- Two private Telegram channels/groups (add your bot as admin) for file logs (`FLOG_CHANNEL`) and user logs (`ULOG_CHANNEL`)

### 2. Clone & install

```bash
git clone <your-repo-url>
cd tg-filestream-bot
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

Open `.env` and set at minimum: `API_ID`, `API_HASH`, `BOT_TOKEN`, `DATABASE_URL`, `OWNER_ID`, `FLOG_CHANNEL`, `ULOG_CHANNEL`, and `FQDN`.

See the comments inside [`.env.example`](./.env.example) for what each variable does.

### 4. Run locally

```bash
python -m FileStream
```

The bot will start polling Telegram, and the aiohttp web server will start on `PORT` (default `8080`), serving the stream/download links.

## 🐳 Run with Docker

```bash
docker build -t filestream-bot .
docker run -d --env-file .env -p 8080:8080 filestream-bot
```

## ☁️ Deploy to Render / Heroku

This repo includes a `Procfile` and `Dockerfile`, so it deploys as-is to platforms like **Render** or **Heroku**:

1. Push the repo to GitHub
2. Create a new Web Service on Render (or app on Heroku) pointing to the repo
3. Add all the environment variables from `.env.example` in the platform's dashboard
4. Set `FQDN` to the domain the platform assigns you (e.g. `your-app-name.onrender.com`)
5. Deploy — the platform will run `python -m FileStream` (via the Procfile) or build via the Dockerfile

> 💡 Free-tier hosts often sleep after inactivity. Set `KEEP_ALIVE_URL` to your own public URL so the bot pings itself periodically and stays awake.

## 🤖 Usage

1. Start a chat with your bot and send `/start`
2. Send it any file (video, document, audio, photo, etc.)
3. The bot replies with a message containing **stream** and **download** links
4. Open the stream link in a browser to watch/play, or the download link to save the file

### Admin Commands

| Command | Description |
|---|---|
| `/status` | Shows total users, banned users, total links generated |
| `/users` | Exports the full user list as a JSON file |
| `/ban` | Ban a user or channel |
| `/unban` | Unban a user or channel |
| `/broadcast` | Send a message to all bot users |

(Admin commands are restricted to `OWNER_ID` / `AUTH_USERS`.)

## ⚠️ Notes

- Keep your `.env` file private — never commit it or your `API_HASH` / `BOT_TOKEN` to version control (`.env` is already in `.gitignore`).
- `FLOG_CHANNEL` and `ULOG_CHANNEL` must be numeric IDs of channels/groups where your bot is an **admin**.
- If `FORCE_UPDATES_CHANNEL=true`, users must join `UPDATES_CHANNEL` before they can use the bot.
