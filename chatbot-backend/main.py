from telebot import TeleBot
import re
import random
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from gejala import gejala_dict
from basis_pengetahuan import basis_pengetahuan
from aturan_inferensi import aturan_inferensi

# API key Telegram Bot
api_key = '5994491197:AAFEhWxSNOSGs8jOTEcZf4-hqnvRvKsjPdE'

# Membuat instance TeleBot
bot = TeleBot(api_key)

# Fungsi Tokenize
def tokenize(text, gejala_dict):
    # Mengubah tanda baca koma dan titik menjadi spasi
    text = re.sub(r'[,.]', ' ', text)

    # Mengubah teks menjadi huruf kecil
    text = text.lower()

    # Tokenisasi menggunakan word_tokenize dari NLTK
    tokens = word_tokenize(text)

    # Menggabungkan gejala yang terdaftar dalam gejala_dict menjadi satu token
    combined_tokens = []
    i = 0
    while i < len(tokens):
        if tokens[i] in gejala_dict:
            combined_tokens.append(gejala_dict[tokens[i]])
            i += 1
        else:
            # Memeriksa apakah ada kombinasi gejala lebih dari dua kata yang terdaftar dalam gejala_dict
            found = False
            for j in range(3, 0, -1):
                if i + j <= len(tokens) and ' '.join(tokens[i:i+j]) in gejala_dict:
                    combined_tokens.append(gejala_dict[' '.join(tokens[i:i+j])])
                    i += j
                    found = True
                    break
            if not found:
                combined_tokens.append(tokens[i])
                i += 1

    return combined_tokens

# Fungsi lemmatisasi
def lemmatize(input_gejala):
    lemmatizer = WordNetLemmatizer()
    lemmatized_gejala = [lemmatizer.lemmatize(gejala) for gejala in input_gejala]
    return lemmatized_gejala

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

            # Menambahkan bobot 1 untuk gejala yang hanya masuk di dalam aturan inferensi
            for penyakit, daftar_gejala in aturan_inferensi.items():
                if penyakit not in solusi and gejala in daftar_gejala:
                    if penyakit not in solusi:
                        solusi[penyakit] = 1
                    else:
                        solusi[penyakit] += 1

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
    input_gejala = tokenize(message.text, gejala_dict)  # Tokenisasi menggunakan fungsi word_tokenize dari NLTK
    input_gejala = [gejala.lower() for gejala in input_gejala]  # Menerapkan case folding pada seluruh inputan
    input_gejala = lemmatize(input_gejala)  # Melakukan lemmatisasi pada kata-kata gejala
    solusi = forward_chaining(input_gejala)
    hasil = tampilkan_hasil(solusi)
    bot.reply_to(message, hasil)
    print(input_gejala)

# Menjalankan bot
bot.polling()
