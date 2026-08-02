import aiohttp
import jinja2
import urllib.parse

from FileStream.config import Telegram, Server
from FileStream.utils.database import Database
from FileStream.utils.human_readable import humanbytes

db = Database(Telegram.DATABASE_URL, Telegram.SESSION_NAME)

async def render_page(db_id, token: str = ""):
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

    if str((file_data['mime_type']).split('/')[0].strip()) == 'video':
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
        file_size=file_size,
        mime_type=mime_type,
        expires_at=expires_at
    )
