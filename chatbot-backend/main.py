from telebot import TeleBot
import re
import random

# API key Telegram Bot
api_key = '5994491197:AAFEhWxSNOSGs8jOTEcZf4-hqnvRvKsjPdE'

# Membuat instance TeleBot
bot = TeleBot(api_key)

# Basis pengetahuan
basis_pengetahuan = {
    'Muntah': {
        'Bulimia Nervosa': 0.7,
        'Anoreksia Nervosa': 0.3,
    },
    'Kelaparan': {
        'Bulimia Nervosa': 0.2,
        'Anoreksia Nervosa': 0.8,
    },
    'Menstruasi': {
        'Bulimia Nervosa': 0.4,
        'Anoreksia Nervosa': 0.6,
    },
    'Makan Berlebihan' : {
        'Bulimia Nervosa': 0.9,
        'Anoreksia Nervosa': 0.1,
    },
    'Diare' : {
        'Bulimia Nervosa': 0.1,
        'Anoreksia Nervosa': 0.9,
    }
}

# Aturan inferensi
aturan_inferensi = {
    'Bulimia Nervosa': ['Muntah', 'Kelaparan', 'Menstruasi', 'Makan Berlebihan'],
    'Anoreksia Nervosa': ['Muntah', 'Kelaparan', 'Menstruasi', 'Diare'],
}

# Fungsi forward chaining
def forward_chaining(input_gejala):
    solusi = {}
    for gejala in input_gejala:
        if gejala in basis_pengetahuan:
            for penyakit, bobot in basis_pengetahuan[gejala].items():
                if penyakit not in solusi:
                    solusi[penyakit] = 0
                solusi[penyakit] += bobot
    for penyakit, daftar_gejala in aturan_inferensi.items():
        if all(gejala in input_gejala for gejala in daftar_gejala) and penyakit not in solusi:
            solusi[penyakit] = 1
    return solusi

# Fungsi untuk menampilkan hasil deteksi penyakit
def tampilkan_hasil(solusi):
    if not solusi:
        return "Tidak ada penyakit yang terdeteksi."
    else:
        penyakit_terdeteksi = max(solusi, key=solusi.get)
        gejala_umum = "Gejala Umum : \n"
        if penyakit_terdeteksi == 'Bulimia Nervosa':
            gejala_umum += "makan berlebihan, menyakiti diri sendiri, muntah, kelaparan, Sakit tenggorokan, pembengkakan pada wajah atau kelenjar di rahang, gangguan siklus, menstruasi, gemuk"
        elif penyakit_terdeteksi == 'Anoreksia Nervosa':
            gejala_umum += "penurunan berat badan, muntah, diare, melakukan diet, kulit kering, rambut rontok, lemas, gangguan siklus menstruasi, sangat kurus"
        penanganan = "Penanganan: \n"
        if penyakit_terdeteksi == 'Bulimia Nervosa':
            penanganan += "Konseling dan terapi."
        elif penyakit_terdeteksi == 'Anoreksia Nervosa':
            penanganan += "Terapi perilaku kognitif."
        return f"Penyakit yang terdeteksi: {penyakit_terdeteksi}\n\n{gejala_umum}\n\n{penanganan}"

# Handler untuk command "/start"
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Selamat datang! Silakan masukkan gejala-gejala penyakit yang Anda alami.")

# Handler untuk semua pesan selain command "/start"
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    input_gejala = message.text.split(", ")
    solusi = forward_chaining(input_gejala)
    hasil = tampilkan_hasil(solusi)
    bot.reply_to(message, hasil)

# Menjalankan bot
bot.polling()
