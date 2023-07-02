from telebot import TeleBot
import re
import os
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from nltk.util import ngrams
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from gejala import gejala_dict
from basis_pengetahuan import basis_pengetahuan
from aturan_inferensi import aturan_inferensi

# API key Telegram Bot
api_key = '5994491197:AAFEhWxSNOSGs8jOTEcZf4-hqnvRvKsjPdE'

# Inisialisasi Stemmer dan Stopwords
stemmer = PorterStemmer()
nltk_stopwords = set(stopwords.words('indonesian'))

# Membuat instance TeleBot
bot = TeleBot(api_key)

# Fungsi Case Folding
def case_folding(text):
    return text.lower()

# Fungsi Tokenisasi
def tokenize(text):
    text = re.sub(r'[,.]', ' ', text)
    tokens = word_tokenize(text)
    return tokens

# Get the absolute path of the stopwords.txt file
stopwords_path = os.path.join(os.path.dirname(__file__), 'stopwords.txt')

def filter_stop_words(tokens):
    filtered_tokens = []
    with open(stopwords_path, 'r') as file:
        stopwords = [line.strip() for line in file]
    
    for token in tokens:
        # Mengecek apakah token ada dalam stopwords
        if token in stopwords:
            continue
        
        # Membuat n-gram dari token
        token_ngrams = [' '.join(gram) for gram in list(ngrams(token.split(), 2))]

        # Memeriksa apakah ada n-gram yang ada dalam gejala_dict
        found = False
        for ngram in token_ngrams:
            if ngram in gejala_dict:
                filtered_tokens.append(ngram)
                found = True
                break

        # Jika tidak ada n-gram yang ada dalam gejala_dict, tambahkan token ke filtered_tokens
        if not found:
            filtered_tokens.append(token)

    return filtered_tokens

# Fungsi Stemming
# def stemming(tokens):
#     stemmed_tokens = []
#     for token in tokens:
#         if token in gejala_dict.keys():
#             stemmed_tokens.append(token)
#         else:
#             stemmed_token = stemmer.stem(token)
#             if stemmed_token in gejala_dict.keys():
#                 stemmed_tokens.append(stemmed_token)
#             else:
#                 stemmed_tokens.append(token)
#     return stemmed_tokens
def stemming(tokens):
    stemmer = StemmerFactory().create_stemmer()
    stemmed_tokens = [stemmer.stem(token) for token in tokens]
    return stemmed_tokens


# # Fungsi Pencarian Keyword
def find_keyword(tokens):
    keywords = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token in gejala_dict:
            keywords.append(token)
        else:
            token_stem = stemmer.stem(token)
            j = i + 1
            while j <= len(tokens):
                phrase = ' '.join(tokens[i:j])
                if phrase in gejala_dict:
                    keywords.append(phrase)
                    i = j - 1
                    break
                j += 1
        i += 1
    return keywords

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
        if penyakit_terdeteksi == 'Depresi':
            gejala_umum += "rasa bersalah, mudah lelah, kurang fokus, sulit tidur, menyakiti diri sendiri, perasaan tidak menentu, murung, tidak percaya diri, tidak berguna, masa depan suram, ingin bunuh diri, perubahan nafsu makan"
        elif penyakit_terdeteksi == 'Gangguan Kecemasan':
            gejala_umum += "kurang fokus, cemas, takut, sulit tidur, mudah lelah, mudah tersinggung, gelisah, sulit mengambil keputusan, sakit kepala, gemetaran, keringat berlebihan, mual, sakit perut"
        elif penyakit_terdeteksi == 'OCD':
            gejala_umum += "rasa bersalah, cemas, waspada berlebihan, pengucapan kata yang tidak berarti, pengulangan kata, pengulangan tindakan, serangan panik, memeriksa sesuatu berulang, mempermasalahkan kerapian, mempermasalahkan keteraturan"
        elif penyakit_terdeteksi == 'Bulimia Nervosa':
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
    input_gejala = message.text

    # Case Folding
    input_gejala = case_folding(input_gejala)
    print("Case Folding :",input_gejala)

    # Tokenisasi
    tokens = tokenize(input_gejala)
    print("Tokenisasi :",tokens)

    # Filtering Stop Words
    filtered_tokens = filter_stop_words(tokens)
    print("Filtering :",filtered_tokens)

    # Stemming
    stemmed_tokens = stemming(filtered_tokens)
    print("Stemming :",stemmed_tokens)

    # Pencarian Keyword
    keywords = find_keyword(stemmed_tokens)
    print("Find Keywords :",keywords)

    # Forward Chaining
    solusi = forward_chaining(keywords)
    print("Proses Forward Chaining :",solusi)

    # Hasil
    hasil = tampilkan_hasil(solusi)

    bot.reply_to(message, hasil)

# Menjalankan bot
bot.polling()
