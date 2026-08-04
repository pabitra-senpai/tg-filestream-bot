import aiohttp
import jinja2
import urllib.parse

from FileStream.config import Telegram, Server
from FileStream.utils.database import Database
from FileStream.utils.human_readable import humanbytes

db = Database(Telegram.DATABASE_URL, Telegram.SESSION_NAME)

# Formats HTML5 <video> can actually decode in mainstream browsers.
# Anything outside this list still opens the watch page (so the VLC / MX
# Player / nPlayer deep-links stay available) — it just doesn't get the
# inline browser player, which would otherwise silently fail to play.
BROWSER_PLAYABLE_EXTENSIONS = {'.mp4', '.m4v', '.webm', '.mov', '.ogv', '.3gp'}

async def render_page(db_id, token: str = "", force_dl: bool = False):
    file_data = await db.get_file(db_id)
    src = urllib.parse.urljoin(Server.URL, f'dl/{file_data["_id"]}')
    if token:
        src = f"{src}?hash={token}"
    file_size = humanbytes(file_data['file_size'])
    file_name = file_data['file_name'].replace("_", " ")
    mime_type = file_data.get('mime_type') or 'video/mp4'

    # Token format is "<expires_at>.<signature>" (see utils/security.py).
    # Pulled out here purely for display (a live countdown) — the actual
    # access control already happened in stream_routes before this runs.
    expires_at = 0
    if token and "." in token:
        try:
            expires_at = int(token.split(".", 1)[0])
        except ValueError:
            expires_at = 0

    is_video = str(file_data.get('mime_type') or '').split('/')[0].strip() == 'video'
    is_image = str(file_data.get('mime_type') or '').split('/')[0].strip() == 'image'

    raw_name = file_data.get('file_name') or ''
    file_ext = ('.' + raw_name.rsplit('.', 1)[-1].lower()) if '.' in raw_name else ''
    is_browser_playable = file_ext in BROWSER_PLAYABLE_EXTENSIONS

    preview_url = None
    if is_image:
        preview_url = urllib.parse.urljoin(Server.URL, f'preview/{file_data["_id"]}')
        if token:
            preview_url = f"{preview_url}?hash={token}"

    thumb_url = None
    if is_video and file_data.get('thumbnail_file_id'):
        thumb_url = urllib.parse.urljoin(Server.URL, f'thumb/{file_data["_id"]}')
        if token:
            thumb_url = f"{thumb_url}?hash={token}"

    if is_video and not force_dl:
        template_file = "FileStream/template/play.html"
    else:
        template_file = "FileStream/template/dl.html"
        async with aiohttp.ClientSession() as s:
            async with s.get(src) as u:
                file_size = humanbytes(int(u.headers.get('Content-Length')))

    with open(template_file) as f:
        template = jinja2.Template(f.read())

    return template.render(
        file_name=file_name,
        file_url=src,
        preview_url=preview_url,
        thumb_url=thumb_url,
        is_browser_playable=is_browser_playable,
        file_size=file_size,
        mime_type=mime_type,
        expires_at=expires_at
    )
