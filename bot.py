import json
import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ==================================================
# SOZLAMALAR
# ==================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 1820874479
ADMIN_USERNAME = "nizomjon_o7"

CARD_NUMBER = "4073 4200 4624 8401"
CARD_OWNER = "N.A."
VIP_PRICE = "29 900 so'm"

MOVIES_FILE = "movies.json"
CHANNELS_FILE = "channels.json"
VIP_FILE = "vip_users.json"


# ==================================================
# JSON FUNKSIYALAR
# ==================================================

def load_json(filename):
    if not os.path.exists(filename):
        return {}

    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# ==================================================
# OBUNANI TEKSHIRISH
# ==================================================

async def check_subscription(user_id, bot):

    channels = load_json(CHANNELS_FILE)

    # Kanal qo'shilmagan bo'lsa
    if not channels:
        return True

    for channel in channels.values():

        try:
            member = await bot.get_chat_member(
                chat_id=channel,
                user_id=user_id
            )

            if member.status not in [
                "member",
                "administrator",
                "creator"
            ]:
                return False

        except Exception as e:
            print("OBUNA XATOSI:", e)
            return False

    return True


def subscription_keyboard():

    channels = load_json(CHANNELS_FILE)

    keyboard = []

    for channel in channels.values():

        username = channel.replace("@", "")

        keyboard.append([
            InlineKeyboardButton(
                f"📢 {channel}",
                url=f"https://t.me/{username}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "✅ Obunani tekshirish",
            callback_data="check_subscription"
        )
    ])

    return InlineKeyboardMarkup(keyboard)


# ==================================================
# ASOSIY MENYU
# ==================================================

def main_menu():

    keyboard = [

        [
            InlineKeyboardButton(
                "🎬 Kino qidirish",
                callback_data="search_movie"
            )
        ],

        [
            InlineKeyboardButton(
                "💎 VIP",
                callback_data="vip"
            )
        ],

        [
            InlineKeyboardButton(
                "👤 Admin bilan bog‘lanish",
                url="https://t.me/nizomjon_o7"
            )
        ]

    ]

    return InlineKeyboardMarkup(keyboard)


# ==================================================
# ADMIN MENYU
# ==================================================

def admin_menu():

    keyboard = [

        [
            InlineKeyboardButton(
                "➕ Kanal qo‘shish",
                callback_data="add_channel"
            ),
            InlineKeyboardButton(
                "🗑 Kanal o‘chirish",
                callback_data="delete_channel"
            )
        ],

        [
            InlineKeyboardButton(
                "📋 Kanallar",
                callback_data="channel_list"
            )
        ],

        [
            InlineKeyboardButton(
                "➕ Kino qo‘shish",
                callback_data="add_movie"
            ),
            InlineKeyboardButton(
                "🗑 Kino o‘chirish",
                callback_data="delete_movie"
            )
        ],

        [
            InlineKeyboardButton(
                "📋 Kinolar",
                callback_data="movie_list"
            )
        ],

        [
            InlineKeyboardButton(
                "💎 VIP foydalanuvchilar",
                callback_data="vip_users"
            )
        ]

    ]

    return InlineKeyboardMarkup(keyboard)


# ==================================================
# START
# ==================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    print("START BOSILDI")

    user_id = update.effective_user.id

    subscribed = await check_subscription(
        user_id,
        context.bot
    )

    if not subscribed:

        await update.message.reply_text(
            "🔐 Botdan foydalanish uchun kanallarga obuna bo‘ling.",
            reply_markup=subscription_keyboard()
        )

        return

    await update.message.reply_text(
        "🎬 Niko KinoUz botiga xush kelibsiz!\n\n"
        "Kerakli bo‘limni tanlang 👇",
        reply_markup=main_menu()
    )


# ==================================================
# ADMIN
# ==================================================

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:

        await update.message.reply_text(
            "❌ Siz admin emassiz."
        )

        return

    context.user_data.clear()

    await update.message.reply_text(
        "⚙️ ADMIN PANEL",
        reply_markup=admin_menu()
    )


# ==================================================
# TUGMALAR
# ==================================================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    print("================================")
    print("🔥 CALLBACK KELDI")
    print("TUGMA:", query.data)
    print("USER:", query.from_user.id)
    print("================================")

    try:
        await query.answer()
    except Exception as e:
        print("QUERY ANSWER XATOSI:", e)

    user_id = query.from_user.id
    data = query.data

    # ==================================================
    # KINO QIDIRISH
    # ==================================================

    if data == "search_movie":

        context.user_data["action"] = "search_movie"

        await query.message.reply_text(
            "🎬 Kino kodini yuboring.\n\n"
            "Masalan:\n"
            "1234"
        )

        return


    # ==================================================
    # VIP
    # ==================================================

    if data == "vip":

        keyboard = [
            [
                InlineKeyboardButton(
                    "📸 Chek yuborish",
                    callback_data="send_receipt"
                )
            ]
        ]

        await query.message.reply_text(
            "💎 VIP OBUNA\n\n"
            f"💰 Narxi: {VIP_PRICE}\n\n"
            f"💳 Karta:\n<code>{CARD_NUMBER}</code>\n\n"
            f"👤 Karta egasi: {CARD_OWNER}\n\n"
            "To‘lovni amalga oshirgach,\n"
            "«📸 Chek yuborish» tugmasini bosing.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return


    # ==================================================
    # CHEK YUBORISH
    # ==================================================

    if data == "send_receipt":

        context.user_data["action"] = "send_receipt"

        await query.message.reply_text(
            "📸 To‘lov chekini yuboring.\n\n"
            "Rasm yoki fayl ko‘rinishida yuborishingiz mumkin."
        )

        return


    # ==================================================
    # OBUNANI TEKSHIRISH
    # ==================================================

    if data == "check_subscription":

        subscribed = await check_subscription(
            user_id,
            context.bot
        )

        if subscribed:

            await query.message.reply_text(
                "✅ Obuna tasdiqlandi!\n\n"
                "🎬 Niko KinoUz botiga xush kelibsiz!",
                reply_markup=main_menu()
            )

        else:

            await query.message.reply_text(
                "❌ Hali barcha kanallarga obuna bo‘lmagansiz.",
                reply_markup=subscription_keyboard()
            )

        return


    # ==================================================
    # ADMIN TEKSHIRISH
    # ==================================================

    if user_id != ADMIN_ID:
        return


    # ==================================================
    # KANAL QO‘SHISH
    # ==================================================

    if data == "add_channel":

        context.user_data["action"] = "add_channel"

        await query.message.reply_text(
            "➕ Kanal username'ini yuboring.\n\n"
            "Masalan:\n"
            "@NikoKinoUz"
        )

        return


    # ==================================================
    # KANAL O‘CHIRISH
    # ==================================================

    if data == "delete_channel":

        context.user_data["action"] = "delete_channel"

        await query.message.reply_text(
            "🗑 O‘chiriladigan kanal username'ini yuboring."
        )

        return


    # ==================================================
    # KANALLAR RO‘YXATI
    # ==================================================

    if data == "channel_list":

        channels = load_json(CHANNELS_FILE)

        if not channels:

            await query.message.reply_text(
                "📋 Hozircha kanal yo‘q."
            )

        else:

            text = "📋 KANALLAR\n\n"

            for key, channel in channels.items():
                text += f"{key}. 📢 {channel}\n"

            await query.message.reply_text(text)

        return


    # ==================================================
    # KINO QO‘SHISH
    # ==================================================

    if data == "add_movie":

        context.user_data["action"] = "add_movie_code"

        await query.message.reply_text(
            "➕ Kino kodini yuboring.\n\n"
            "Masalan:\n"
            "1234"
        )

        return


    # ==================================================
    # KINO O‘CHIRISH
    # ==================================================

    if data == "delete_movie":

        context.user_data["action"] = "delete_movie"

        await query.message.reply_text(
            "🗑 O‘chiriladigan kino kodini yuboring."
        )

        return


    # ==================================================
    # KINOLAR RO‘YXATI
    # ==================================================

    if data == "movie_list":

        movies = load_json(MOVIES_FILE)

        if not movies:

            await query.message.reply_text(
                "📋 Hozircha kino yo‘q."
            )

        else:

            text = "📋 KINOLAR\n\n"

            for code in movies:
                text += f"🎬 {code}\n"

            await query.message.reply_text(text)

        return


    # ==================================================
    # VIP FOYDALANUVCHILAR
    # ==================================================

    if data == "vip_users":

        vip_users = load_json(VIP_FILE)

        if not vip_users:

            await query.message.reply_text(
                "💎 VIP foydalanuvchilar yo‘q."
            )

        else:

            text = "💎 VIP FOYDALANUVCHILAR\n\n"

            for user_id in vip_users:
                text += f"👤 {user_id}\n"

            await query.message.reply_text(text)

        return


# ==================================================
# VIP ADMIN TASDIQLASH
# ==================================================

async def vip_admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    data = query.data


    # ==================================================
    # VIP BERISH
    # ==================================================

    if data.startswith("approve_vip_"):

        user_id = data.replace(
            "approve_vip_",
            ""
        )

        vip_users = load_json(VIP_FILE)

        vip_users[str(user_id)] = True

        save_json(
            VIP_FILE,
            vip_users
        )

        try:

            await context.bot.send_message(
                chat_id=int(user_id),
                text=(
                    "🎉 TABRIKLAYMIZ!\n\n"
                    "💎 Sizga VIP obuna tasdiqlandi."
                )
            )

        except Exception as e:

            print("VIP XABAR XATOSI:", e)

        await query.message.reply_text(
            f"✅ VIP berildi!\n\n"
            f"User ID: {user_id}"
        )

        return


    # ==================================================
    # VIP RAD ETISH
    # ==================================================

    if data.startswith("reject_vip_"):

        user_id = data.replace(
            "reject_vip_",
            ""
        )

        try:

            await context.bot.send_message(
                chat_id=int(user_id),
                text=(
                    "❌ VIP to‘lovingiz tasdiqlanmadi."
                )
            )

        except Exception as e:

            print("RAD XABAR XATOSI:", e)

        await query.message.reply_text(
            f"❌ To‘lov rad etildi.\n\n"
            f"User ID: {user_id}"
        )

        return


# ==================================================
# XABARLARNI QABUL QILISH
# ==================================================

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    user_id = update.effective_user.id
    action = context.user_data.get("action")


    # ==================================================
    # VIP CHEK
    # ==================================================

    if action == "send_receipt":

        caption = (
            "💎 YANGI VIP TO‘LOV\n\n"
            f"👤 Ism: {update.effective_user.full_name}\n"
            f"🆔 ID: {user_id}\n"
            f"💰 Summa: {VIP_PRICE}\n\n"
            "⬇️ Chek:"
        )

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "✅ VIP BERISH",
                    callback_data=f"approve_vip_{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "❌ RAD ETISH",
                    callback_data=f"reject_vip_{user_id}"
                )
            ]
        ])


        # RASM
        if update.message.photo:

            photo = update.message.photo[-1]

            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=photo.file_id,
                caption=caption,
                reply_markup=keyboard
            )

            await update.message.reply_text(
                "✅ Chek adminga yuborildi.\n\n"
                "⏳ Admin tasdiqlashini kuting."
            )

            context.user_data["action"] = None

            return


        # FAYL
        if update.message.document:

            await context.bot.send_document(
                chat_id=ADMIN_ID,
                document=update.message.document.file_id,
                caption=caption,
                reply_markup=keyboard
            )

            await update.message.reply_text(
                "✅ Chek adminga yuborildi.\n\n"
                "⏳ Admin tasdiqlashini kuting."
            )

            context.user_data["action"] = None

            return


        await update.message.reply_text(
            "❌ Iltimos, chekni rasm yoki fayl ko‘rinishida yuboring."
        )

        return


    # ==================================================
    # ADMIN — KANAL QO‘SHISH
    # ==================================================

    if user_id == ADMIN_ID and action == "add_channel":

        if not update.message.text:
            await update.message.reply_text(
                "❌ Kanal username'ini matn ko‘rinishida yuboring."
            )
            return

        channel = update.message.text.strip()

        if not channel.startswith("@"):
            channel = "@" + channel

        channels = load_json(CHANNELS_FILE)

        exists = False

        for value in channels.values():

            if value.lower() == channel.lower():
                exists = True
                break

        if exists:

            await update.message.reply_text(
                "⚠️ Bu kanal allaqachon qo‘shilgan."
            )

        else:

            new_id = str(
                max(
                    [int(x) for x in channels.keys()],
                    default=0
                ) + 1
            )

            channels[new_id] = channel

            save_json(
                CHANNELS_FILE,
                channels
            )

            await update.message.reply_text(
                f"✅ Kanal qo‘shildi: {channel}\n\n"
                "⚠️ Endi botni ushbu kanalga administrator qiling."
            )

        context.user_data["action"] = None

        return


    # ==================================================
    # ADMIN — KANAL O‘CHIRISH
    # ==================================================

    if user_id == ADMIN_ID and action == "delete_channel":

        if not update.message.text:
            return

        channel = update.message.text.strip()

        if not channel.startswith("@"):
            channel = "@" + channel

        channels = load_json(CHANNELS_FILE)

        found = None

        for key, value in channels.items():

            if value.lower() == channel.lower():
                found = key
                break

        if found:

            del channels[found]

            save_json(
                CHANNELS_FILE,
                channels
            )

            await update.message.reply_text(
                "🗑 Kanal o‘chirildi."
            )

        else:

            await update.message.reply_text(
                "❌ Kanal topilmadi."
            )

        context.user_data["action"] = None

        return


    # ==================================================
    # ADMIN — KINO KODI
    # ==================================================

    if user_id == ADMIN_ID and action == "add_movie_code":

        if not update.message.text:
            await update.message.reply_text(
                "❌ Kino kodini yuboring."
            )
            return

        code = update.message.text.strip()

        context.user_data["movie_code"] = code
        context.user_data["action"] = "add_movie_file"

        await update.message.reply_text(
            f"🎬 Kino kodi: {code}\n\n"
            "Endi kinoni VIDEO qilib yuboring."
        )

        return


    # ==================================================
    # ADMIN — KINO VIDEO
    # ==================================================

    if user_id == ADMIN_ID and action == "add_movie_file":

        if update.message.video:

            code = context.user_data.get("movie_code")

            if not code:
                await update.message.reply_text(
                    "❌ Kino kodi topilmadi. Qaytadan urinib ko‘ring."
                )
                context.user_data.clear()
                return

            movies = load_json(MOVIES_FILE)

            movies[code] = update.message.video.file_id

            save_json(
                MOVIES_FILE,
                movies
            )

            await update.message.reply_text(
                f"✅ Kino muvaffaqiyatli saqlandi!\n\n"
                f"🎬 Kod: {code}"
            )

            context.user_data["action"] = None
            context.user_data["movie_code"] = None

        else:

            await update.message.reply_text(
                "❌ Iltimos, kinoni VIDEO ko‘rinishida yuboring."
            )

        return


    # ==================================================
    # ADMIN — KINO O‘CHIRISH
    # ==================================================

    if user_id == ADMIN_ID and action == "delete_movie":

        if not update.message.text:
            return

        code = update.message.text.strip()

        movies = load_json(MOVIES_FILE)

        if code in movies:

            del movies[code]

            save_json(
                MOVIES_FILE,
                movies
            )

            await update.message.reply_text(
                f"🗑 {code} kodi bilan kino o‘chirildi."
            )

        else:

            await update.message.reply_text(
                "❌ Bunday kino topilmadi."
            )

        context.user_data["action"] = None

        return


    # ==================================================
    # FOYDALANUVCHI KINO QIDIRADI
    # ==================================================

    if action == "search_movie":

        context.user_data["action"] = None

        subscribed = await check_subscription(
            user_id,
            context.bot
        )

        if not subscribed:

            await update.message.reply_text(
                "🔐 Avval kanallarga obuna bo‘ling.",
                reply_markup=subscription_keyboard()
            )

            return

        if not update.message.text:
            return

        code = update.message.text.strip()

        movies = load_json(MOVIES_FILE)

        if code in movies:

            await update.message.reply_video(
                video=movies[code],
                caption=(
                    f"🎬 Kino kodi: {code}\n\n"
                    "🍿 Yoqimli tomosha!"
                )
            )

        else:

            await update.message.reply_text(
                "❌ Bunday kino topilmadi."
            )

        return


    # ==================================================
    # ODDIY KOD ORQALI QIDIRISH
    # ==================================================

    if update.message.text:

        code = update.message.text.strip()

        movies = load_json(MOVIES_FILE)

        if code in movies:

            subscribed = await check_subscription(
                user_id,
                context.bot
            )

            if not subscribed:

                await update.message.reply_text(
                    "🔐 Avval kanallarga obuna bo‘ling.",
                    reply_markup=subscription_keyboard()
                )

                return

            await update.message.reply_video(
                video=movies[code],
                caption=(
                    f"🎬 Kino kodi: {code}\n\n"
                    "🍿 Yoqimli tomosha!"
                )
            )

        else:

            await update.message.reply_text(
                "❌ Kino kodi topilmadi.\n\n"
                "🎬 Kino kodini tekshirib qayta yuboring."
            )


# ==================================================
# XATO
# ==================================================

async def error_handler(update, context):

    print("================================")
    print("❌ BOT XATOSI:")
    print(context.error)
    print("================================")


# ==================================================
# MAIN
# ==================================================

def main():

    app = Application.builder().token(BOT_TOKEN).build()


    # START
    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )


    # ADMIN
    app.add_handler(
        CommandHandler(
            "admin",
            admin
        )
    )


    # VIP ADMIN
    app.add_handler(
        CallbackQueryHandler(
            vip_admin_handler,
            pattern=r"^(approve_vip_|reject_vip_)"
        )
    )


    # BARCHA TUGMALAR
    app.add_handler(
        CallbackQueryHandler(
            button_handler
        )
    )


    # XABARLAR
    app.add_handler(
        MessageHandler(
            filters.ALL & ~filters.COMMAND,
            message_handler
        )
    )


    # XATOLAR
    app.add_error_handler(
        error_handler
    )


    print("🤖 Niko KinoUz bot ishga tushdi!")
    print("👤 Admin ID:", ADMIN_ID)

    app.run_polling()


# ==================================================
# ISHGA TUSHIRISH
# ==================================================

if __name__ == "__main__":
    main()