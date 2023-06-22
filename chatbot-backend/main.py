from telebot import TeleBot
import re
import random
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

# API key Telegram Bot
api_key = '5994491197:AAFEhWxSNOSGs8jOTEcZf4-hqnvRvKsjPdE'

# Membuat instance TeleBot
bot = TeleBot(api_key)

# Basis pengetahuan
basis_pengetahuan = {
    'muntah': {
        'Bulimia Nervosa': 0.7,
        'Anoreksia Nervosa': 0.3,
    },
    'kelaparan': {
        'Bulimia Nervosa': 0.2,
        'Anoreksia Nervosa': 0.8,
    },
    'menstruasi': {
        'Bulimia Nervosa': 0.4,
        'Anoreksia Nervosa': 0.6,
    },
    'makan berlebihan' : {
        'Bulimia Nervosa': 0.9,
        'Anoreksia Nervosa': 0.1,
    },
    'diare' : {
        'Bulimia Nervosa': 0.3,
        'Anoreksia Nervosa': 0.7,
    }
}

# Aturan inferensi
aturan_inferensi = {
    'Bulimia Nervosa': ['muntah', 'kelaparan', 'menstruasi', 'makan berlebihan'],
    'Anoreksia Nervosa': ['muntah', 'kelaparan', 'menstruasi', 'diare', 'makan berlebihan'],
}

#Fungsi Tokenize
def tokenize(text):
    # Menggunakan regular expression untuk mengekstrak gejala sebagai satu token
    gejala_pattern = r"(?i)\b(makan berlebihan)\b"  # Tambahkan gejala lain yang perlu diidentifikasi di sini
    gejala_matches = re.findall(gejala_pattern, text)
    
    # Menghapus gejala dari teks untuk memperoleh token lainnya
    text_without_gejala = re.sub(gejala_pattern, '', text)
    
    # Tokenisasi menggunakan word_tokenize dari NLTK untuk token-token lainnya
    tokens = word_tokenize(text_without_gejala)
    
    # Menggabungkan token gejala dengan token-token lainnya
    tokens.extend(gejala_matches)
    
    return tokens


# Fungsi stemming
def stemming(input_gejala):
    stemmer = PorterStemmer()
    stemmed_gejala = [stemmer.stem(gejala) for gejala in input_gejala]
    return stemmed_gejala


# Fungsi forward chaining
def forward_chaining(input_gejala):
    solusi = {}
    for penyakit, daftar_gejala in aturan_inferensi.items():
        if all(gejala in input_gejala for gejala in daftar_gejala):
            solusi[penyakit] = 1

    if not solusi:
        for gejala in input_gejala:
            gejala = gejala.lower()  # Menerapkan case folding
            if gejala in basis_pengetahuan:
                for penyakit, bobot in basis_pengetahuan[gejala].items():
                    if penyakit not in solusi:
                        solusi[penyakit] = 0
                    if penyakit in solusi:
                        solusi[penyakit] += bobot

    return solusi


# Fungsi untuk menampilkan hasil deteksi penyakit
def tampilkan_hasil(solusi):
    if not solusi:
        return "Tidak ada penyakit yang terdeteksi."
    else:
        penyakit_terdeteksi = max(solusi, key=solusi.get)
        gejala_umum = "Gejala Umum:\n"
        if penyakit_terdeteksi == 'Bulimia Nervosa':
            gejala_umum += "makan berlebihan, menyakiti diri sendiri, muntah, kelaparan, Sakit tenggorokan, pembengkakan pada wajah atau kelenjar di rahang, gangguan siklus, menstruasi, gemuk"
        elif penyakit_terdeteksi == 'Anoreksia Nervosa':
            gejala_umum += "penurunan berat badan, muntah, diare, melakukan diet, kulit kering, rambut rontok, lemas, gangguan siklus menstruasi, sangat kurus"
        penanganan = "Penanganan:\n"
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
    input_gejala = tokenize(message.text)  # Tokenisasi menggunakan fungsi word_tokenize dari NLTK
    input_gejala = [gejala.lower() for gejala in input_gejala]  # Menerapkan case folding pada seluruh inputan
    input_gejala = stemming(input_gejala)  # Melakukan stemming pada kata-kata gejala
    solusi = forward_chaining(input_gejala)
    hasil = tampilkan_hasil(solusi)
    bot.reply_to(message, hasil)
    print(input_gejala)

# Menjalankan bot
bot.polling()
