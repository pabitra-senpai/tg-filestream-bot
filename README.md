<div align="center">

<img src="assets/bot_icon.png" alt="FileStream" width="64" />

# FileStream

### Turn any Telegram file into an instant, secure stream or download link.

*A [Nex](https://t.me/NexBotz) product*

[![Python](https://img.shields.io/badge/Python-3.10+-F59E0B?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Pyrogram](https://img.shields.io/badge/Pyrogram-Async-F59E0B?style=flat-square)](https://docs.pyrogram.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Database-10B981?style=flat-square&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-MIT-8B5CF6?style=flat-square)](#license)
[![Telegram](https://img.shields.io/badge/Telegram-Nex_FileStreamBot-26A5E4?style=flat-square&logo=telegram&logoColor=white)](https://t.me/Nex_FileStreamBot)

</div>

---

## About

**FileStream** is a self-hosted Telegram bot that turns any file you send it — video, audio,
document, whatever — into a direct link you can stream in your browser or download at full
speed. No forwarding to public channels, no third-party file hosts. Your files stay in your own
private Telegram log channel, served through your own web server, protected by
**cryptographically signed, auto-expiring links**.

## ✨ Features

- 🎬 **In-browser streaming** — full HTML5 video player powered by [Vime](https://vimejs.com/), with play/pause, seek, volume, captions, playback speed, fullscreen & picture-in-picture
- ⚡ **High-speed downloads** — Range-request support for resumable, unthrottled transfers
- 🔐 **Signed, expiring links** — every stream/download URL is HMAC-SHA256 signed and expires automatically (default: 6 hours) — no more permanently-guessable links
- 📱 **External player deep links** — open straight in VLC, MX Player, or nPlayer on mobile
- 🚫 **Force-subscribe support** — require users to join your channel before use
- 🛠️ **Admin panel** — live dashboard stats, paginated file/user tables, ban/unban, broadcast
- ⚙️ **Multi-client load balancing** — spread traffic across multiple bot tokens
- 🐳 **Deploy-ready** — Docker, Render, and Heroku configs included out of the box

## 🧱 Tech Stack

| Layer | Technology |
|---|---|
| Bot Framework | [Pyrofork](https://github.com/Mayuri-Chan/pyrofork) (Pyrogram fork) |
| Web Server | aiohttp |
| Database | MongoDB |
| Video Player | [Vime](https://vimejs.com/) (official web components, via jsDelivr CDN) |
| Templating | Jinja2 |
| Deployment | Docker / Render / Heroku |

## 🚀 Quick Start

### 1. Clone & install

```bash
git clone https://github.com/pabitra-senpai/filestream-bot.git
cd filestream-bot
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Fill in `.env` — see [Environment Variables](#-environment-variables) below for what each one does.

### 3. Run

```bash
python3 -m FileStream
```

### Docker

```bash
docker build -t filestream-bot .
docker run --env-file .env -p 8080:8080 filestream-bot
```

### Deploy to Render

Push this repo to your own GitHub, connect it on [Render](https://render.com), set the
environment variables from `.env.example` in the dashboard, and deploy. The included
`render.yaml` / `Procfile` handle the rest.

## 🔧 Environment Variables

<details>
<summary><strong>Telegram credentials & bot identity</strong></summary>

| Variable | Description |
|---|---|
| `API_ID` / `API_HASH` | From [my.telegram.org](https://my.telegram.org) |
| `BOT_TOKEN` | From [@BotFather](https://t.me/BotFather) |
| `OWNER_ID` | Your numeric Telegram user ID |
| `AUTH_USERS` | Extra user IDs allowed to use the bot (space-separated) |

</details>

<details>
<summary><strong>Database & logging</strong></summary>

| Variable | Description |
|---|---|
| `DATABASE_URL` | MongoDB connection string |
| `FLOG_CHANNEL` | Private channel ID where files are logged/stored |
| `ULOG_CHANNEL` | Private channel ID where user activity/errors are logged |

</details>

<details>
<summary><strong>Force-subscribe</strong></summary>

| Variable | Description |
|---|---|
| `UPDATES_CHANNEL` | Channel username (no `@`) users must join |
| `FORCE_SUB_ID` | Optional channel ID override |
| `FORCE_UPDATES_CHANNEL` | `true` / `false` |

</details>

<details>
<summary><strong>Web server & link security</strong></summary>

| Variable | Description |
|---|---|
| `PORT` / `BIND_ADDRESS` | Server listen address |
| `FQDN` | Your public domain (no `https://`, no trailing slash) |
| `HAS_SSL` / `NO_PORT` | Domain/URL formatting flags |
| `SECRET_KEY` | HMAC signing secret — generate with `python3 -c "import secrets; print(secrets.token_hex(32))"` |
| `LINK_EXPIRY_SECONDS` | How long generated links stay valid (default `21600` = 6h) |

</details>

<details>
<summary><strong>Bot images</strong></summary>

| Variable | Description |
|---|---|
| `FILE_PIC` | Thumbnail shown with generated file links |
| `START_PICS` | Comma-separated images rotated on `/start` |
| `VERIFY_PIC` | Image shown on the force-subscribe prompt |

</details>

Full list with inline comments is in [`.env.example`](.env.example).

## 🤖 Bot Commands

| Command | Description |
|---|---|
| `/start` | Start the bot & see what it can do |
| `/help` | How to use FileStream |
| `/about` | About this bot |
| `/files` | View your recently uploaded files |

Admin-only commands (`/status`, `/ban`, `/unban`, `/broadcast`, `/del`, `/users`, `/setcmd`) are
gated behind `OWNER_ID` / `AUTH_USERS` and intentionally **not** exposed in the public bot menu.

## 🔒 Security

Every `/watch/{id}` and `/dl/{id}` link is signed with **HMAC-SHA256** and carries an embedded
expiry timestamp — see [`utils/security.py`](FileStream/utils/security.py). Requests with a
missing, tampered, or expired token are rejected before any file data is served, and shown a
branded "Link Expired" page instead of a raw HTTP error. Nothing about a file is guessable from
its URL alone.

## 📁 Project Structure

```
FileStream/
├── bot/plugins/     → start.py, stream.py, admin.py, callback.py
├── server/          → stream_routes.py (aiohttp file server + auth)
├── utils/           → database.py, security.py, file_properties.py, bot_utils.py
├── template/         → play.html, dl.html, link_expired.html
├── config.py         → environment configuration
└── __main__.py       → entry point (bot + web server)
```

## 🙌 Credits

Built and maintained under **[Nex](https://t.me/NexBotz)** — follow the channel for updates,
new bot launches, and support.

## 📄 License

MIT — see [`LICENSE`](LICENSE) for details.

---

<div align="center">
<sub><img src="assets/bot_icon.png" alt="FileStream" width="16" /> FileStream · Personal Stream Service · Do Not Share Publicly</sub>
</div>
