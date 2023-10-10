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
def stemming(tokens):
    stemmer = StemmerFactory().create_stemmer()
    stemmed_tokens = [stemmer.stem(token) for token in tokens]
    return stemmed_tokens


# Fungsi Pencarian Keyword
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

# Handler untuk command "/start"
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Selamat datang! Silakan masukkan gejala-gejala penyakit yang Anda alami.")

# # Handler untuk semua pesan selain command "/start"
# @bot.message_handler(func=lambda message: True)
# def handle_message(message):
#     input_gejala = message.text

#     # Case Folding
#     input_gejala = case_folding(input_gejala)
#     print("Case Folding :",input_gejala)

#     # Tokenisasi
#     tokens = tokenize(input_gejala)
#     print("Tokenisasi :",tokens)

#     # Filtering Stop Words
#     filtered_tokens = filter_stop_words(tokens)
#     print("Filtering :",filtered_tokens)

#     # Stemming
#     stemmed_tokens = stemming(filtered_tokens)
#     print("Stemming :",stemmed_tokens)

#     # Pencarian Keyword
#     keywords = find_keyword(stemmed_tokens)
#     print("Find Keywords :",keywords)
    
#     # Gabungkan semua tahap ke dalam satu pesan
#     output_message = f"Case Folding: {input_gejala}\n\n" \
#                      f"Tokenisasi: {tokens}\n\n" \
#                      f"Filtering: {filtered_tokens}\n\n" \
#                      f"Stemming: {stemmed_tokens}\n\n" \
#                      f"Find Keywords: {keywords}"

#     bot.send_message(message.chat.id, output_message)

    # # Forward Chaining
    # solusi = forward_chaining(keywords)
    # print("Proses Forward Chaining :",solusi)

    # # Hasil
    # hasil = tampilkan_hasil(solusi)

    # bot.reply_to(message, hasil)

# Inisialisasi variabel untuk logika pertanyaan
gejala_belum_ditanyakan = set(gejala_dict.keys())  # Gejala yang belum ditanyakan
input_gejala = []  # Gejala yang sudah diinput oleh pengguna
penyakit_mungkin = []  # Daftar penyakit yang mungkin

# Implementasi Forward Chaining
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
        return "Tidak ada penyakit yang terdeteksi. Silahkan berikan gejala yang lain, yang anda alami."
    else:
        penyakit_terdeteksi = max(solusi, key=solusi.get)
        deskripsi_penyakit = "Deskripsi Penyakit:\n"
        if penyakit_terdeteksi == 'Depresi':
            deskripsi_penyakit += "Depresi adalah gangguan mental yang ditandai oleh perasaan sedih yang berkepanjangan, kehilangan minat atau kegairahan terhadap aktivitas yang biasanya dinikmati, dan penurunan energi atau kelelahan."
        elif penyakit_terdeteksi == 'Gangguan Kecemasan':
            deskripsi_penyakit += "Gangguan kecemasan adalah kondisi mental yang ditandai oleh kecemasan yang berlebihan, persisten, dan mengganggu dalam kehidupan sehari-hari."
        elif penyakit_terdeteksi == 'OCD':
            deskripsi_penyakit += "Obsessive-Compulsive Disorder (OCD) adalah gangguan kecemasan yang ditandai oleh pola pikir obsesif yang mengganggu dan tindakan kompulsif yang dilakukan untuk mengurangi kecemasan atau ketidaknyamanan yang muncul akibat obsesi tersebut."
        elif penyakit_terdeteksi == 'PTSD':
            deskripsi_penyakit += "PTSD (Post-Traumatic Stress Disorder) adalah gangguan mental yang terjadi setelah seseorang mengalami atau menyaksikan peristiwa traumatis yang mengancam jiwa atau menyakitkan secara emosional. Peristiwa traumatis tersebut bisa berupa kecelakaan serius, bencana alam, kekerasan fisik atau seksual, peperangan, atau pengalaman traumatis lainnya."
        elif penyakit_terdeteksi == 'Gangguan Kepribadian Paranoid':
            deskripsi_penyakit += "Gangguan Kepribadian Paranoid adalah jenis gangguan kepribadian yang ditandai oleh pola pikir dan perilaku yang berlebihan atau yang tidak beralasan yang mencerminkan ketidakpercayaan dan kecurigaan terhadap orang lain. Individu dengan gangguan kepribadian paranoid cenderung merasa dicurigai, didorong oleh keyakinan yang tidak beralasan bahwa orang-orang di sekitarnya memiliki motif tersembunyi atau berniat jahat terhadap mereka."
        elif penyakit_terdeteksi == 'Gangguan Kepribadian Narsistik':
            deskripsi_penyakit += "Gangguan Kepribadian Narsistik adalah jenis gangguan kepribadian yang ditandai oleh pola perilaku yang berlebihan dan terus-menerus memperlihatkan kebutuhan yang berlebihan akan pengakuan, keagungan, dan perhatian yang berlebihan terhadap diri sendiri. Individu dengan gangguan kepribadian narsistik cenderung memiliki pandangan yang melebih-lebihkan tentang kemampuan dan prestasi mereka sendiri, seringkali merasa lebih penting daripada orang lain, dan mengharapkan perlakuan istimewa."
        elif penyakit_terdeteksi == 'Bulimia Nervosa':
            deskripsi_penyakit += "Bulimia Nervosa adalah gangguan makan yang ditandai oleh pola makan yang tidak terkendali secara berulang (makan berlebihan) diikuti oleh perilaku kompensasi yang tidak sehat. Orang yang mengalami bulimia nervosa seringkali merasa kehilangan kendali saat makan dan berusaha untuk mengendalikan berat badan mereka dengan cara yang tidak sehat, seperti memuntahkan makanan atau menggunakan obat pencahar."
        elif penyakit_terdeteksi == 'Anoreksia Nervosa':
            deskripsi_penyakit += "Anoreksia Nervosa adalah gangguan makan yang ditandai oleh perasaan takut yang kuat terhadap berat badan dan bentuk tubuh yang menyebabkan perilaku makan yang tidak sehat. Orang yang mengalami anoreksia nervosa cenderung memiliki persepsi yang tidak realistis tentang tubuh mereka dan berusaha untuk menjaga berat badan mereka serendah mungkin dengan cara yang tidak sehat."
        # ... Deskripsi untuk penyakit lainnya ...

        gejala_umum = "Gejala Umum:\n"
        if penyakit_terdeteksi == 'Depresi':
            gejala_umum += "1. merasa bersalah, \n 2. mudah lelah, \n 3. kurang fokus, \n 4. sulit tidur, \n 5.menyakiti diri sendiri, \n 6.perasaan tidak menentu, \n 7. murung, \n 8. tidak percaya diri, \n 9. tidak berguna, \n 10. masa depan suram, \n 11. ingin bunuh diri, \n 12. perubahan nafsu makan"
        elif penyakit_terdeteksi == 'Gangguan Kecemasan':
            gejala_umum += "1. kurang fokus, \n 2. cemas, \n 3. takut, \n 4. sulit tidur, \n 5. mudah lelah, \n 6. mudah tersinggung, \n 7. gelisah, \n 8. sulit mengambil keputusan, \n 9. sakit kepala, \n 10. gemetaran, \n 11. keringat berlebihan, \n 12. mual, \n 13. sakit perut"
        elif penyakit_terdeteksi == 'OCD':
            gejala_umum += "1. rasa bersalah \n2. cemas \n3. waspada berlebihan \n4. pengucapan kata yang tidak berarti \n5. pengulangan kata \n6. pengulangan tindakan \n7. serangan panik \n8. memeriksa sesuatu berulang \n9. mempermasalahkan kerapian \n10. mempermasalahkan keteraturan"
        elif penyakit_terdeteksi == 'PTSD':
            gejala_umum += "1. ingatan kejadian masa lalu yang menakutkan \n2. sering bermimpi buruk \n3. menghindari tempat atau hal yang berkaitan dengan kejadian traumatis \n4. sulit untuk tidur \n5. takut \n6. sulit berkonsentrasi"
        elif penyakit_terdeteksi == 'Gangguan Kepribadian Paranoid':
            gejala_umum += "1. meragukan komitmen \n2. tidak percaya dengan orang lain \n3. tidak mudah memaafkan \n4. sangat sensitif terhadap kritikan \n5. selalu merasa benar \n6. keras kepala"
        elif penyakit_terdeteksi == 'Gangguan Kepribadian Narsistik':
            gejala_umum += "1. merasa lebih baik dari orang lain \n2. membutuhkan banyak pujian \n3. sibuk menghayal \n4. merasa istimewa \n5. tidak memiliki empati dan kepedulian \n6. iri \n7. sombong"
        elif penyakit_terdeteksi == 'Bulimia Nervosa':
            gejala_umum += "1. makan berlebihan \n2. menyakiti diri sendiri \n3. muntah \n4. kelaparan \n5. sakit tenggorokan \n6. pembengkakan pada wajah atau kelenjar di rahang \n7. gangguan siklus \n8. menstruasi \n9. gemuk \n10. mengkonsumsi obat pencahar"
        elif penyakit_terdeteksi == 'Anoreksia Nervosa':
            gejala_umum += "1. penurunan berat badan \n2. muntah \n3. diare \n4. melakukan diet \n5. kulit kering \n6. rambut rontok \n7. lemas \n8. gangguan siklus menstruasi \n9. sangat kurus"
        # ... Gejala umum untuk penyakit lainnya ...

        penanganan = "Penanganan:\n"
        if penyakit_terdeteksi == 'Depresi':
            penanganan += "lebih banyak melakukan aktifitas aktifitas positif, konsumsi makan makanan yang sehat, tidur yang cukup, lebih menerima dan menghadapi permasalahan yang ada, melakukan hal hal yang menyenangkan"
        elif penyakit_terdeteksi == 'Gangguan Kecemasan':
            penanganan += "menjaga kebugaran tubuh dengan melakukan olahraga teratur, melakukan relaksasi atau merilekskan tubuh, menghindari kafein, menghindari rokok, tidak mengkonsumsi minuman keras atau minuman beralkohol."
        elif penyakit_terdeteksi == 'OCD':
            penanganan += "kelompok dukungan, terapi perilaku kognitif, terapi aversi, psikoedukasi, terapi perilaku, emotif rasional, pajanan dan pencegahan respons, psikoterapi, desensitisasi sistematik, psikoterapi kelompok"
        elif penyakit_terdeteksi == 'PTSD':
            penanganan += "terapi perilaku kognitif, pajanan dan pencegahan respons, pemrosesan ulang dan desensitisasi gerakan mata, terapi paparan"
        elif penyakit_terdeteksi == 'Gangguan Kepribadian Paranoid':
            penanganan += "terapi perilaku kognitif, terapi psikodinamik, terapi interpersonal."
        elif penyakit_terdeteksi == 'Gangguan Kepribadian Narsistik':
            penanganan += "terapi bicara, terapi perilaku kognitif, terapi psikodinamik, terapi interpersonal"
        elif penyakit_terdeteksi == 'Bulimia Nervosa':
            penanganan += " kelompok dukungan, terapi perilaku kognitif, terapi kognitif, terapi perilaku, dialektis, konseling psikologis, psikoedukasi, terapi keluarga, terapi perilaku, psikoterapi."
        elif penyakit_terdeteksi == 'Anoreksia Nervosa':
            penanganan += "kelompok dukungan, terapi perilaku kognitif, terapi perilaku dialektis, konseling psikologis, psikoterapi interpersonal, terapi keluarga, terapi perilaku, psikoterapi, psikoterapi singkat, psikoterapi kelompok"
        # ... Penanganan untuk penyakit lainnya ...

        return f"Penyakit yang terdeteksi: {penyakit_terdeteksi}\n\n{deskripsi_penyakit}\n\n{gejala_umum}\n\n{penanganan}"
    
 # Handler untuk semua pesan selain command "/start"
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    global gejala_belum_ditanyakan, input_gejala, penyakit_mungkin

    # Jika masih ada gejala yang belum ditanyakan
    if gejala_belum_ditanyakan:
        # Ambil gejala berikutnya
        gejala_selanjutnya = gejala_belum_ditanyakan.pop()

        # Tanyakan kepada pengguna
        bot.reply_to(message, f"Apakah Anda mengalami gejala '{gejala_selanjutnya}'? (Ya/Tidak)")

        # Tambahkan gejala ke input pengguna jika pengguna menjawab 'Ya'
        @bot.message_handler(func=lambda message: message.text.lower() == 'ya')
        def handle_yes_response(message):
            # Simpan gejala yang dikonfirmasi oleh pengguna
            gejala_terkonfirmasi = gejala_selanjutnya.lower()
            input_gejala.append(gejala_terkonfirmasi)
            
            # Periksa gejala yang cocok dalam aturan inferensi
            penyakit_terkait = []

            for penyakit, daftar_gejala in aturan_inferensi.items():
                if gejala_terkonfirmasi in daftar_gejala:
                    penyakit_terkait.append(penyakit)

            # Periksa gejala yang sudah diinput oleh pengguna
            gejala_sudah_diinput = set(input_gejala)

            # Cari gejala yang perlu dikonfirmasi dari aturan inferensi yang belum dikonfirmasi oleh pengguna
            gejala_yang_perlu_dikonfirmasi = [
                gejala
                for penyakit in penyakit_terkait
                for gejala in aturan_inferensi[penyakit]
                if gejala.lower() not in gejala_sudah_diinput
            ]

            if gejala_yang_perlu_dikonfirmasi:
                # Tanyakan gejala selanjutnya dari aturan inferensi yang belum dikonfirmasi
                gejala_selanjutnya = gejala_yang_perlu_dikonfirmasi.pop(0)
                bot.reply_to(message, f"Apakah Anda mengalami gejala '{gejala_selanjutnya}'? (Ya/Tidak)")
            else:
                # Jika tidak ada lagi gejala yang perlu dikonfirmasi, lanjutkan dengan diagnosa
                input_gejala = case_folding(' '.join(input_gejala))  # Menggabungkan gejala yang sudah diinput
                solusi = forward_chaining(input_gejala)  # Lakukan forward chaining
                hasil_diagnosa = tampilkan_hasil(solusi)  # Tampilkan hasil diagnosa

                # Reset gejala yang belum ditanyakan, input gejala, dan penyakit yang mungkin
                gejala_belum_ditanyakan = set(gejala_dict.keys())
                input_gejala = []
                penyakit_mungkin = []

                # Kirim hasil diagnosa ke pengguna
                bot.reply_to(message, hasil_diagnosa)

    elif len(input_gejala) >= 3:
        # Jika sudah ada minimal 3 gejala yang diinput oleh pengguna
        input_gejala = case_folding(' '.join(input_gejala))  # Menggabungkan gejala yang sudah diinput
        solusi = forward_chaining(input_gejala)  # Lakukan forward chaining
        hasil_diagnosa = tampilkan_hasil(solusi)  # Tampilkan hasil diagnosa

        # Reset gejala yang belum ditanyakan, input gejala, dan penyakit yang mungkin
        gejala_belum_ditanyakan = set(gejala_dict.keys())
        input_gejala = []
        penyakit_mungkin = []

        # Kirim hasil diagnosa ke pengguna
        bot.reply_to(message, hasil_diagnosa)

# Menjalankan bot
bot.polling()