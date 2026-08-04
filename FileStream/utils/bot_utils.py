from pyrogram.errors import UserNotParticipant, FloodWait
from pyrogram.enums.parse_mode import ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from FileStream.utils.translation import LANG
from FileStream.utils.database import Database
from FileStream.utils.human_readable import humanbytes
from FileStream.config import Telegram, Server
from FileStream.bot import FileStream
import asyncio
import math
from typing import Union
from datetime import datetime, timezone, timedelta

# Max characters shown per file name inside the /files caption before truncating
FILES_NAME_MAX_LEN = 26  # keeps "<idx>. <name>..." on a single line on narrow mobile screens
# Numbered buttons per row in the /files keyboard
FILES_BUTTONS_PER_ROW = 4

# ✅ Indian Standard Time (IST)
IST = timezone(timedelta(hours=5, minutes=30))

# Database
db = Database(Telegram.DATABASE_URL, Telegram.SESSION_NAME)

# Invite Link
async def get_invite_link(bot, chat_id: Union[str, int]):
    try:
        invite_link = await bot.create_chat_invite_link(chat_id=chat_id)
        return invite_link
    except FloodWait as e:
        print(f"Sleep of {e.value}s caused by FloodWait ...")
        await asyncio.sleep(e.value)
        return await get_invite_link(bot, chat_id)

# Force Sub Check
async def is_user_joined(bot, message: Message):
    if Telegram.FORCE_SUB_ID and Telegram.FORCE_SUB_ID.startswith("-100"):
        channel_chat_id = int(Telegram.FORCE_SUB_ID)
    elif Telegram.FORCE_SUB_ID and (not Telegram.FORCE_SUB_ID.startswith("-100")):
        channel_chat_id = Telegram.FORCE_SUB_ID
    else:
        return 200
    try:
        user = await bot.get_chat_member(chat_id=channel_chat_id, user_id=message.from_user.id)
        if user.status == "BANNED":
            await message.reply_text(
                text=LANG.BAN_TEXT.format(Telegram.OWNER_ID),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            return False
    except UserNotParticipant:
        invite_link = await get_invite_link(bot, chat_id=channel_chat_id)
        if Telegram.VERIFY_PIC:
            ver = await message.reply_photo(
                photo=Telegram.VERIFY_PIC,
                caption="<i><b>Jᴏɪɴ Mʏ Uᴘᴅᴀᴛᴇ Cʜᴀɴɴᴇʟ Tᴏ Usᴇ Mᴇ 🔐</b></i>",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton("❆ Jᴏɪɴ Oᴜʀ Cʜᴀɴɴᴇʟ ❆", url=invite_link.invite_link)
                ]]
                )
            )
        else:
            ver = await message.reply_text(
                text="<b><i>Jᴏɪɴ Mʏ Uᴘᴅᴀᴛᴇ Cʜᴀɴɴᴇʟ Tᴏ Usᴇ Mᴇ 🔐</i></b>",
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton("❆ Jᴏɪɴ Oᴜʀ Cʜᴀɴɴᴇʟ ❆", url=invite_link.invite_link)
                    ]]
                ),
                parse_mode=ParseMode.HTML
            )
        await asyncio.sleep(30)
        try:
            await ver.delete()
            await message.delete()
        except Exception:
            pass
        return False
    except Exception:
        await message.reply_text(
            text=f"<b><i>Sᴏᴍᴇᴛʜɪɴɢ Wʀᴏɴɢ! \nCᴏɴᴛᴀᴄᴛ Mʏ Dᴇᴠᴇʟᴏᴘᴇʀ</i> <a href='https://t.me/{Telegram.UPDATES_CHANNEL}'>[ Cʟɪᴄᴋ Hᴇʀᴇ ]</a></b>",
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True)
        return False
    return True

# Private Gen Link
async def gen_link(_id):
    file_info = await db.get_file(_id)
    file_name = file_info['file_name']
    file_size = humanbytes(file_info['file_size'])
    mime_type = file_info['mime_type']

    page_link = f"{Server.URL}go/watch/{_id}"
    download_page_link = f"{Server.URL}go/download/{_id}"
    file_link = f"https://t.me/{FileStream.username}?start=file_{_id}"

    if "video" in (mime_type or ""):
        stream_text = LANG.STREAM_TEXT.format(file_name, file_size, download_page_link, page_link, file_link)
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("📹 Sᴛʀᴇᴀᴍ", url=page_link), InlineKeyboardButton("Dᴏᴡɴʟᴏᴀᴅ", url=download_page_link)],
                [InlineKeyboardButton("📂 Gᴇᴛ Fɪʟᴇ", url=file_link), InlineKeyboardButton("Rᴇᴠᴏᴋᴇ Fɪʟᴇ", callback_data=f"msgdelpvt_{_id}")],
                [
                    InlineKeyboardButton("📤 Sʜᴀʀᴇ", url=f"https://t.me/share/url?url={file_link}&text=Check%20out%20this%20file%20on%20{FileStream.username}!"),
                    InlineKeyboardButton("❌ Cʟᴏsᴇ", callback_data="close")
                ]
            ]
        )
    else:
        stream_text = LANG.STREAM_TEXT_X.format(file_name, file_size, download_page_link, file_link)
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("📥 Dᴏᴡɴʟᴏᴀᴅ", url=download_page_link)],
                [InlineKeyboardButton("📂 Gᴇᴛ Fɪʟᴇ", url=file_link), InlineKeyboardButton("Rᴇᴠᴏᴋᴇ Fɪʟᴇ", callback_data=f"msgdelpvt_{_id}")],
                [
                    InlineKeyboardButton("📤 Sʜᴀʀᴇ", url=f"https://t.me/share/url?url={file_link}&text=Check%20out%20this%20file%20on%20{FileStream.username}!"),
                    InlineKeyboardButton("❌ Cʟᴏsᴇ", callback_data="close")
                ]
            ]
        )
    return reply_markup, stream_text

# Channel Gen Link
async def gen_linkx(m: Message, _id, name: list):
    file_info = await db.get_file(_id)
    file_name = file_info['file_name']
    mime_type = file_info['mime_type']
    file_size = humanbytes(file_info['file_size'])

    page_link = f"{Server.URL}go/watch/{_id}"
    download_page_link = f"{Server.URL}go/download/{_id}"
    file_link = f"https://t.me/{FileStream.username}?start=file_{_id}"

    if "video" in (mime_type or ""):
        stream_text = LANG.STREAM_TEXT_X.format(file_name, file_size, download_page_link, page_link)
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("📹 Sᴛʀᴇᴀᴍ", url=page_link), InlineKeyboardButton("📥 Dᴏᴡɴʟᴏᴀᴅ", url=download_page_link)]
            ]
        )
    else:
        stream_text = LANG.STREAM_TEXT_X.format(file_name, file_size, download_page_link, file_link)
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("📥 Dᴏᴡɴʟᴏᴀᴅ", url=download_page_link)]
            ]
        )
    return reply_markup, stream_text

# User Banned
async def is_user_banned(message):
    if await db.is_user_banned(message.from_user.id):
        await message.reply_text(
            text=LANG.BAN_TEXT.format(Telegram.OWNER_ID),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        return True
    return False

# Channel Banned
async def is_channel_banned(bot, message):
    if await db.is_user_banned(message.chat.id):
        await bot.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=message.id,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(f"🚫 Cʜᴀɴɴᴇʟ Is Bᴀɴɴᴇᴅ", callback_data="N/A")]])
        )
        return True
    return False

# User Authorized
async def is_user_authorized(message):
    if hasattr(Telegram, 'AUTH_USERS') and Telegram.AUTH_USERS:
        user_id = message.from_user.id

        if user_id == Telegram.OWNER_ID:
            return True

        if not (user_id in Telegram.AUTH_USERS):
            await message.reply_text(
                text="<b><i>Yᴏᴜ Aʀᴇ Nᴏᴛ Aᴜᴛʜᴏʀɪᴢᴇᴅ Tᴏ Usᴇ Tʜɪs Bᴏᴛ.</b></i>",
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            return False

    return True

# User Exist
async def is_user_exist(bot, message):
    user = message.from_user
    if not user:
        return
        
    # Safely get username
    username = user.username if user.username else "None"
    
    # Check if user is in DB
    if not bool(await db.get_user(user.id)):
        # Pass ID, Name, and Username to DB
        await db.add_user(user.id, user.first_name, username)
        
        # ✅ New User Log Logic
        now = datetime.now(IST)
        date = now.strftime("%d/%m/%y")
        time = now.strftime("%I:%M.%S %p")
        
        # Ensure we have bot username
        bot_username = bot.username if hasattr(bot, 'username') and bot.username else (await bot.get_me()).username

        log_text = (
            f"**⌬ #NewUser 🆕👤**\n"
            f"**┟ Bot:** __@{bot_username}__\n"
            f"**┟ User:** __[{user.first_name}](tg://user?id={user.id})__\n"
            f"**┟ User ID:** `{user.id}`\n"
            f"**┟ Date:** __{date}__\n"
            f"**┖ Time:** __{time}__"
        )

        await bot.send_message(Telegram.ULOG_CHANNEL, log_text)
    else:
        # Update existing user info (Self-Healing)
        await db.update_user_info(user.id, user.first_name, username)

# Channel Exist
async def is_channel_exist(bot, message):
    chat_id = message.chat.id
    title = message.chat.title
    # Safely get username for channel
    username = message.chat.username if message.chat.username else "None"

    if not bool(await db.get_user(chat_id)):
        # Pass ID, Title (as Name), and Username to DB
        await db.add_user(chat_id, title, username)
        members = await bot.get_chat_members_count(chat_id)
        
        # ✅ New Channel Log Logic
        now = datetime.now(IST)
        date = now.strftime("%d/%m/%y")
        time = now.strftime("%I:%M.%S %p")
        
        # Ensure we have bot username
        bot_username = bot.username if hasattr(bot, 'username') and bot.username else (await bot.get_me()).username

        # Handle 'Added By' field safely
        adder_name = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})" if message.from_user else "Unknown (Channel Admin)"

        log_text = (
            f"**⌬ #NewChannel 🆕👥**\n"
            f"**┟ Bot:** __@{bot_username}__\n"
            f"**┟ Added By:** __{adder_name}__\n"
            f"**┟ Chat Name:** __{title}__\n"
            f"**┟ Chat ID:** `{chat_id}`\n"
            f"**┟ Total Members:** __{members}__\n"
            f"**┟ Date:** __{date}__\n"
            f"**┖ Time:** __{time}__"
        )

        await bot.send_message(Telegram.ULOG_CHANNEL, log_text)

# Verify User
async def verify_user(bot, message):
    if not await is_user_authorized(message):
        return False

    if await is_user_banned(message):
        return False

    await is_user_exist(bot, message)

    if Telegram.FORCE_SUB:
        if not await is_user_joined(bot, message):
            return False

    return True

# Truncate a long file name for compact display
def truncate_file_name(name: str, max_len: int = FILES_NAME_MAX_LEN) -> str:
    if not name:
        return "Unknown"
    if len(name) <= max_len:
        return name
    return name[:max_len - 3].rstrip() + "..."

# Build the compact "/files" caption + numbered/paginated keyboard
# Reused by both the /files command (start.py) and the userfiles_X
# pagination callback (callback.py) so both stay in sync.
async def gen_files_caption_and_keyboard(file_list_no: int, user_id: int):
    file_range = [file_list_no * 10 - 10 + 1, file_list_no * 10]
    user_files, total_files = await db.find_files(user_id, file_range)

    files = [x async for x in user_files]

    caption_lines = ["**🗂 Yᴏᴜʀ Fɪʟᴇs**", "", f"**📁 Tᴏᴛᴀʟ Fɪʟᴇs :** `{total_files}`", ""]
    if files:
        for idx, x in enumerate(files, start=1):
            caption_lines.append(f"{idx}. {truncate_file_name(x['file_name'])}")
    else:
        caption_lines.append("ᴇᴍᴘᴛʏ")
    caption = "\n".join(caption_lines)

    keyboard = []
    row = []
    for idx, x in enumerate(files, start=1):
        row.append(InlineKeyboardButton(str(idx), callback_data=f"myfile_{x['_id']}_{file_list_no}"))
        if len(row) == FILES_BUTTONS_PER_ROW:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    if total_files > 10:
        keyboard.append([
            InlineKeyboardButton("◀ Pʀᴇᴠ", callback_data=f"userfiles_{file_list_no-1}" if file_list_no > 1 else "N/A"),
            InlineKeyboardButton(f"{file_list_no}/{math.ceil(total_files / 10)}", callback_data="N/A"),
            InlineKeyboardButton("Nᴇxᴛ ▶", callback_data=f"userfiles_{file_list_no+1}" if total_files > file_list_no * 10 else "N/A")
        ])

    keyboard.append([InlineKeyboardButton("✖ Cʟᴏsᴇ", callback_data="close")])

    return caption, InlineKeyboardMarkup(keyboard), total_files
