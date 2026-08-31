import os
import time
from pathlib import Path

import edge_tts

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)


TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

ALLOWED_CHAT_ID = 167186163

VOICE = "fa-IR-FaridNeural"

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)


SPEEDS = {
    "speed_075": ("0.75×", "-25%"),
    "speed_100": ("1.0×", "+0%"),
    "speed_125": ("1.25×", "+25%"),
    "speed_150": ("1.5×", "+50%"),
    "speed_200": ("2.0×", "+100%"),
}


async def generate_voice(text, rate):

    filename = (
        DOWNLOAD_DIR
        / f"voice_{int(time.time() * 1000)}.mp3"
    )

    communicate = edge_tts.Communicate(
        text=text,
        voice=VOICE,
        rate=rate,
    )

    await communicate.save(
        str(filename)
    )

    return filename


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_chat.id != ALLOWED_CHAT_ID:
        return

    context.user_data["speed"] = "+0%"

    keyboard = [
        [
            InlineKeyboardButton(
                "▶️ شروع",
                callback_data="start_bot"
            )
        ]
    ]

    await update.message.reply_text(
        "🎙 Persian Voice Bot\n\n"
        "برای شروع روی دکمه زیر بزن:",
        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )


async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    if query.message.chat.id != ALLOWED_CHAT_ID:
        return

    data = query.data

    # -------------------------
    # START
    # -------------------------

    if data == "start_bot":

        keyboard = [
            [
                InlineKeyboardButton(
                    "🐢 0.75×",
                    callback_data="speed_075"
                ),
                InlineKeyboardButton(
                    "🎙 1×",
                    callback_data="speed_100"
                ),
            ],
            [
                InlineKeyboardButton(
                    "⚡ 1.25×",
                    callback_data="speed_125"
                ),
                InlineKeyboardButton(
                    "🚀 1.5×",
                    callback_data="speed_150"
                ),
            ],
            [
                InlineKeyboardButton(
                    "🔥 2×",
                    callback_data="speed_200"
                )
            ]
        ]

        await query.edit_message_text(
            "🎙 صدای فارسی: Farid\n\n"
            "⚡ سرعت را انتخاب کن:",
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

        return

    # -------------------------
    # SPEED
    # -------------------------

    if data in SPEEDS:

        speed_name, speed_value = SPEEDS[data]

        context.user_data["speed"] = speed_value

        keyboard = [
            [
                InlineKeyboardButton(
                    "⚡ تغییر سرعت",
                    callback_data="change_speed"
                )
            ]
        ]

        await query.edit_message_text(
            "✅ ربات آماده است.\n\n"
            "🎙 صدا: Farid\n"
            f"⚡ سرعت: {speed_name}\n\n"
            "حالا متن فارسی خودت را بفرست.",
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

        return

    # -------------------------
    # CHANGE SPEED
    # -------------------------

    if data == "change_speed":

        keyboard = [
            [
                InlineKeyboardButton(
                    "🐢 0.75×",
                    callback_data="speed_075"
                ),
                InlineKeyboardButton(
                    "🎙 1×",
                    callback_data="speed_100"
                ),
            ],
            [
                InlineKeyboardButton(
                    "⚡ 1.25×",
                    callback_data="speed_125"
                ),
                InlineKeyboardButton(
                    "🚀 1.5×",
                    callback_data="speed_150"
                ),
            ],
            [
                InlineKeyboardButton(
                    "🔥 2×",
                    callback_data="speed_200"
                )
            ]
        ]

        await query.edit_message_text(
            "⚡ سرعت جدید را انتخاب کن:",
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )


async def text_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_chat.id != ALLOWED_CHAT_ID:
        return

    text = update.message.text.strip()

    if not text:
        return

    speed = context.user_data.get(
        "speed"
    )

    if speed is None:

        await update.message.reply_text(
            "ابتدا /start را بزن و ربات را شروع کن."
        )

        return

    await update.message.reply_text(
        "🎙 در حال ساخت فایل صوتی..."
    )

    file = None

    try:

        file = await generate_voice(
            text,
            speed
        )

        with open(
            file,
            "rb"
        ) as audio:

            await update.message.reply_audio(
                audio=audio,
                filename="persian_voice.mp3",
                title="Persian Voice"
            )

    except Exception as e:

        print(
            "VOICE ERROR:",
            repr(e)
        )

        await update.message.reply_text(
            "❌ خطا در ساخت فایل صوتی:\n\n"
            + str(e)
        )

    finally:

        if file:

            file.unlink(
                missing_ok=True
            )


def main():

    if not TOKEN:

        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is missing."
        )

    app = (
        Application
        .builder()
        .token(TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            button_handler
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_handler
        )
    )

    print(
        "PERSIAN VOICE BOT IS RUNNING..."
    )

    app.run_polling()


if __name__ == "__main__":
    main()
