import logging
import pandas as pd
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# === AYARLAR ===
BOT_TOKEN = "8446624973:AAFjd5GRqhhnSUmBcHyRSr8ifqbC4jaAApg"  # BotFather token'in (tırnak içinde!)
EXCEL_DOSYA_ADI = "price list (1).xlsx"
DESEN_KOLONU = "DESEN"

# === LOG ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# === EXCEL YÜKLE ===
def fiyat_tablosunu_yukle():
    df = pd.read_excel(EXCEL_DOSYA_ADI)
    df[DESEN_KOLONU] = (
        df[DESEN_KOLONU]
        .astype(str)
        .str.strip()
        .str.upper()
    )
    return df


def fmt_number(value):
    if pd.isna(value) or value == "":
        return ""
    try:
        n = float(value)
        # Tam sayı ise direkt göster, değilse 2 basamak virgüllü (Türk formatı)
        if n.is_integer():
            return f"{int(n)}"
        else:
            return f"{n:.2f}".replace(".", ",")
    except:
        return str(value)


DF = fiyat_tablosunu_yukle()

# === KOMUTLAR ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mesaj = (
        "Merhaba 👋\n"
        "Desen kodunu yaz, sana o desene ait fiyat seçeneklerini göstereyim.\n"
        "Örnek: `0004D-01`"
    )
    await update.message.reply_text(mesaj, parse_mode="Markdown")


async def desen_sorgu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    kod_giris = update.message.text.strip()
    kod = kod_giris.upper()

    if not kod or len(kod) < 2:
        return

    eslesen = DF[DF[DESEN_KOLONU] == kod]

    if eslesen.empty:
        await update.message.reply_text(
            f"'{kod_giris}' için kayıt bulunamadı ❌\n"
            f"Lütfen desen kodunu kontrol et."
        )
        return

    cevap_satirlari = [f"🔎 *{kod}* için kayıtlar:\n"]

    for _, row in eslesen.iterrows():
        desen_adi = str(row.get("DESEN ADI", "") or "").strip()
        mamul_islem = str(row.get("MAMÜL İŞLEMLER", "") or "").strip()
        konstr = str(row.get("KONSTR", "") or "").strip()
        sat_gr = str(row.get("SAT.GR/MT²", "") or "").strip()

        maliyet = fmt_number(row.get("MALİYET", ""))
        ihracat = fmt_number(row.get("İHRACAT ($/MT)", ""))
        yuzde35 = fmt_number(row.get("%35", ""))

        satir_satirlari = []

        # Başlıklar (bold + düzenli)
        if desen_adi:
            satir_satirlari.append(f"• *DESEN ADI:* {desen_adi}")
        if mamul_islem:
            satir_satirlari.append(f"• *MAMÜL İŞLEMLER:* {mamul_islem}")
        if konstr:
            satir_satirlari.append(f"• *KONSTR:* {konstr}")
        if sat_gr:
            satir_satirlari.append(f"• *SAT.GR/MT²:* {sat_gr}")

        # Fiyatlar ($ ile)
        fiyat_parcalari = []
        if maliyet:
            fiyat_parcalari.append(f"Maliyet: {maliyet} $")
        if ihracat:
            fiyat_parcalari.append(f"İhracat ($/MT): {ihracat} $")
        if yuzde35:
            fiyat_parcalari.append(f"%35: {yuzde35} $")

        if fiyat_parcalari:
            satir_satirlari.append(
                "• *MALİYET / İHRACAT / %35:* " + " | ".join(fiyat_parcalari)
            )

        if satir_satirlari:
            cevap_satirlari.append("\n".join(satir_satirlari) + "\n")

    cevap_metni = "\n".join(cevap_satirlari).strip()
    await update.message.reply_text(cevap_metni, parse_mode="Markdown")


# === BOTU BAŞLAT ===
def main():
    print("Bot başlıyor...")
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, desen_sorgu))

    print("Bot çalışıyor, Telegram'dan deneyebilirsin.")
    app.run_polling()


if __name__ == "__main__":
    main()
