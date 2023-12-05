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

api_key = '5994491197:AAFEhWxSNOSGs8jOTEcZf4-hqnvRvKsjPdE'
stemmer = PorterStemmer()
nltk_stopwords = set(stopwords.words('indonesian'))
bot = TeleBot(api_key)

def case_folding(text):
    return text.lower()

def tokenize(text):
    text = re.sub(r'[,.]', ' ', text)
    tokens = word_tokenize(text)
    return tokens

stopwords_path = os.path.join(os.path.dirname(__file__), 'stopwords.txt')

def filter_stop_words(tokens):
    filtered_tokens = []
    with open(stopwords_path, 'r') as file:
        stopwords = [line.strip() for line in file]

    for token in tokens:
        if token in stopwords:
            continue
        token_ngrams = [' '.join(gram) for gram in list(ngrams(token.split(), 2))]
        found = False
        for ngram in token_ngrams:
            if ngram in gejala_dict:
                filtered_tokens.append(ngram)
                found = True
                break
        if not found:
            filtered_tokens.append(token)
    return filtered_tokens

def stemming(tokens):
    stemmer = StemmerFactory().create_stemmer()
    stemmed_tokens = [stemmer.stem(token) for token in tokens]
    return stemmed_tokens

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

def forward_chaining(input_gejala):
    hasil_diagnosa = {}

    for penyakit, gejala_penyakit in aturan_inferensi.items():
        # Hitung jumlah gejala terpilih yang baru ditambahkan oleh pengguna
        jumlah_gejala_terpilih = len(set(input_gejala) & set(gejala_penyakit))

        # Hitung peluang dengan mempertimbangkan gejala baru
        total_gejala_penyakit = len(gejala_penyakit)
        peluang = (jumlah_gejala_terpilih / total_gejala_penyakit) * 100

        hasil_diagnosa[penyakit] = {
            'Peluang': f'{peluang:.2f}%',
            'Gejala penyakit yang diinputkan user': list(set(input_gejala) & set(gejala_penyakit)),
            'Total gejala': jumlah_gejala_terpilih
        }

    return hasil_diagnosa

def tampilkan_hasil(hasil_diagnosa):
    if not hasil_diagnosa:
        return "Tidak ada penyakit yang terdeteksi. Silahkan berikan gejala yang lain, yang anda alami."
    penyakit_terdeteksi = max(hasil_diagnosa, key=lambda x: float(hasil_diagnosa[x]['Peluang'][:-1]))
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
        penanganan += "kelompok dukungan, terapi perilaku kognitif, terapi kognitif, terapi perilaku, dialektis, konseling psikologis, psikoedukasi, terapi keluarga, terapi perilaku, psikoterapi."
    elif penyakit_terdeteksi == 'Anoreksia Nervosa':
        penanganan += "kelompok dukungan, terapi perilaku kognitif, terapi perilaku dialektis, konseling psikologis, psikoterapi interpersonal, terapi keluarga, terapi perilaku, psikoterapi, psikoterapi singkat, psikoterapi kelompok"

    return f"Penyakit yang terdeteksi: {penyakit_terdeteksi}\n" \
           f"Peluang: {hasil_diagnosa[penyakit_terdeteksi]['Peluang']}\n\n" \
           f"{deskripsi_penyakit}\n" \
           f"{gejala_umum}\n" \
           f"{penanganan}\n\n" \
           f"Apabila presentase diagnosis anda dibawah 80%, anda harus menghubungi untuk menanyakan hasil diagnosis lebih lanjut kepada ahli psikolog atau konseling di PENS."
           
def text_mining(input_text):
    # Case Folding
    input_gejala = case_folding(input_text)

    # Tokenisasi
    tokens = tokenize(input_gejala)

    # Filtering Stop Words
    filtered_tokens = filter_stop_words(tokens)

    # Stemming
    stemmed_tokens = stemming(filtered_tokens)

    # Pencarian Keyword
    keywords = find_keyword(stemmed_tokens)

    return keywords

# Tambahkan variabel global untuk menyimpan gejala sebelumnya
penyakit_terdeteksi = ""
gejala_tanya = ""
gejala_sebelumnya = []

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    global gejala_tanya
    global penyakit_terdeteksi
    global gejala_sebelumnya

    if message.text == "/start":
        gejala_tanya = ""
        penyakit_terdeteksi = ""
        gejala_sebelumnya = []  # Tambahkan inisialisasi gejala_sebelumnya
        user_name = message.from_user.username  # Ambil nama pengguna Telegram
        bot.reply_to(message, f"Halo, {user_name}! Selamat Datang di Chatbot Layanan Konseling Mahasiswa PENS. Saya akan membantu Anda mendiagnosa kondisi mental Anda. Silakan berikan gejala yang Anda alami.")
    elif message.text == "/informasi":
        user_name = message.from_user.username  # Ambil nama pengguna Telegram
        reply_message = f"Halo, {user_name}! Selamat datang di Layanan Konseling Mahasiswa PENS. Kami di sini untuk membantu Anda mengatasi berbagai tantangan mental dan emosional yang mungkin Anda alami selama masa studi Anda di PENS."

        reply_message += "\n\nLayanan Konseling PENS menawarkan dukungan emosional dan konseling profesional kepada semua mahasiswa. Apakah Anda menghadapi tekanan akademis, masalah pribadi, atau hanya butuh seseorang untuk diajak berbicara, kami di sini untuk membantu."

        reply_message += "\n\nCara menggunakan layanan kami:"
        reply_message += "\n1. Ketik '/start' untuk memulai konsultasi."
        reply_message += "\n2. Berikan gejala atau ceritakan perasaan Anda."
        reply_message += "\n3. Kami akan melakukan diagnosa dan memberikan saran atau dukungan sesuai kebutuhan Anda."

        reply_message += "\n\nIngatlah bahwa semua sesi konseling bersifat pribadi dan rahasia. Kami peduli dengan kesejahteraan mental Anda, dan kami siap membantu Anda. Jangan ragu untuk berbagi apa yang Anda rasakan."

        reply_message += "\n\nTerima kasih telah menggunakan Layanan Konseling PENS. Jika Anda memiliki pertanyaan lebih lanjut, ketik '/bantuan'."

        bot.reply_to(message, reply_message)
    elif message.text == "/bantuan":
        user_name = message.from_user.username  # Ambil nama pengguna Telegram
        reply_message = f"Halo, {user_name}! Berikut adalah beberapa perintah yang dapat Anda gunakan untuk berinteraksi dengan Layanan Konseling Mahasiswa PENS:"

        reply_message += "\n\n1. `/start`: Memulai sesi konsultasi untuk mendiagnosa kondisi mental Anda."
        reply_message += "\n2. `/informasi`: Menyediakan informasi tentang Layanan Konseling PENS dan cara menggunakannya."
        reply_message += "\n3. `/bantuan`: Menampilkan pesan bantuan ini."

        reply_message += "\n\nIngat, kami di sini untuk membantu Anda. Jika Anda memiliki pertanyaan lebih lanjut atau membutuhkan dukungan tambahan, jangan ragu untuk berbicara dengan kami. Hubungi alamat email layanankonseling@pens.ac.id"

        bot.reply_to(message, reply_message)
    else:
        gejala_sebelumnya.append(message.text)
        
        # Gabungkan semua gejala sebelumnya dengan gejala terbaru
        semua_gejala = ' '.join(gejala_sebelumnya)
        print("Semua Gejala:", semua_gejala)

        # Gabungkan semua gejala sebelumnya dengan gejala terbaru
        input_gejala = case_folding(semua_gejala)
        print("Case Folding:", input_gejala)

        # Tokenisasi
        tokens = tokenize(input_gejala)
        print("Tokenisasi:", tokens)

        # Filtering Stop Words
        filtered_tokens = filter_stop_words(tokens)
        print("Filtering:", filtered_tokens)

        # Stemming
        stemmed_tokens = stemming(filtered_tokens)
        print("Stemming:", stemmed_tokens)

        # Pencarian Keyword
        keywords = find_keyword(stemmed_tokens)
        print("Find Keywords:", keywords)

        # Masukkan ke dalam proses diagnosa
        hasil_diagnosa = forward_chaining(keywords)

        # Jika belum ada gejala yang unggul, atau masih dalam proses pengumpulan gejala
        if not penyakit_terdeteksi or gejala_tanya:
            
            input_gejala = case_folding(input_gejala)
            print("Case Folding:", input_gejala)

            # Tokenisasi
            tokens = tokenize(input_gejala)
            print("Tokenisasi:", tokens)

            # Filtering Stop Words
            filtered_tokens = filter_stop_words(tokens)
            print("Filtering:", filtered_tokens)

            # Stemming
            stemmed_tokens = stemming(filtered_tokens)
            print("Stemming:", stemmed_tokens)

            # Pencarian Keyword
            keywords = find_keyword(stemmed_tokens)
            print("Find Keywords:", keywords)

            hasil_diagnosa = forward_chaining(keywords)

            # Jika masih dalam proses pengumpulan gejala
            if gejala_tanya:
                if hasil_diagnosa and hasil_diagnosa.get(gejala_tanya) and hasil_diagnosa.get(penyakit_terdeteksi) and hasil_diagnosa[gejala_tanya]['Peluang'] == hasil_diagnosa[penyakit_terdeteksi]['Peluang']:
                    # Jika peluang masih sama, tanyakan lagi apakah ada gejala lain
                    bot.reply_to(message, f"Apakah Anda mengalami gejala lain yang masih berhubungan dengan penyakit ini? Jika tidak ada, maka sebutkan kembali gejala yang sering anda alami.")
                else:
                    # Jika peluang berbeda atau gejala_tanya tidak ada, tampilkan hasil
                    response = "Hasil Diagnosa:\n"
                    for penyakit, info in hasil_diagnosa.items():
                        peluang = info['Peluang']
                        gejala_user = info['Gejala penyakit yang diinputkan user']
                        total_gejala = info['Total gejala']

                        response += f"Peluang terkena {penyakit}: {peluang}\n"
                        response += f"Gejala penyakit {penyakit} yang diinputkan user: {gejala_user}\n"
                        response += f"Total gejala {penyakit}: {total_gejala}\n\n"

                    # bot.reply_to(message, response)
                    print(message, response)
                    response = tampilkan_hasil(hasil_diagnosa)
                    bot.reply_to(message, response)

                    # Setelah menampilkan hasil, update penyakit_terdeteksi jika ditemukan
                    penyakit_terdeteksi = max(hasil_diagnosa, key=lambda x: float(hasil_diagnosa[x]['Peluang'][:-1]))
                    gejala_tanya = ""
                    penyakit_terdeteksi = ""
                    gejala_sebelumnya = []

            else:
                # Jika belum ada penyakit_terdeteksi, atau masih dalam proses pengumpulan gejala
                highest_percentage = max(hasil_diagnosa.values(), key=lambda x: float(x['Peluang'][:-1]))['Peluang']
                highest_percentage = float(highest_percentage[:-1])
                
                if highest_percentage == 0:
                    bot.reply_to(message, "Gejala yang dimasukkan tidak valid atau tidak sesuai dengan penyakit apapun. Silakan periksa kembali gejala yang Anda berikan.")
                elif highest_percentage in [float(info['Peluang'][:-1]) for info in hasil_diagnosa.values()]: 
                    # Jika peluang masih sama, tanyakan lagi apakah ada gejala lain
                    gejala_tanya = max(hasil_diagnosa, key=lambda x: float(hasil_diagnosa[x]['Peluang'][:-1]))
                    bot.reply_to(message, f"Apakah Anda mengalami gejala lain yang masih berhubungan dengan penyakit ini? Jika tidak ada, maka sebutkan kembali gejala yang sering anda alami.")
                else:
                    # Jika peluang berbeda, tampilkan hasil
                    response = "Hasil Diagnosa:\n"
                    for penyakit, info in hasil_diagnosa.items():
                        peluang = info['Peluang']
                        gejala_user = info['Gejala penyakit yang diinputkan user']
                        total_gejala = info['Total gejala']

                        response += f"Peluang terkena {penyakit}: {peluang}\n"
                        response += f"Gejala penyakit {penyakit} yang diinputkan user: {gejala_user}\n"
                        response += f"Total gejala {penyakit}: {total_gejala}\n\n"

                    # bot.reply_to(message, response)
                    print(message, response)
                    response = tampilkan_hasil(hasil_diagnosa)
                    bot.reply_to(message, response)

                    # Setelah menampilkan hasil, update penyakit_terdeteksi jika ditemukan
                    penyakit_terdeteksi = max(hasil_diagnosa, key=lambda x: float(hasil_diagnosa[x]['Peluang'][:-1]))
                    gejala_tanya = ""
                    penyakit_terdeteksi = ""
                    gejala_sebelumnya = []

        else:
            # Jika sudah ada hasil unggul, tampilkan hasil tanpa bertanya lagi
            input_gejala = case_folding(input_gejala)
            print("Case Folding:", input_gejala)

            # Tokenisasi
            tokens = tokenize(input_gejala)
            print("Tokenisasi:", tokens)

            # Filtering Stop Words
            filtered_tokens = filter_stop_words(tokens)
            print("Filtering:", filtered_tokens)

            # Stemming
            stemmed_tokens = stemming(filtered_tokens)
            print("Stemming:", stemmed_tokens)

            # Pencarian Keyword
            keywords = find_keyword(stemmed_tokens)
            print("Find Keywords:", keywords)
            hasil_diagnosa = forward_chaining(keywords)
            response = "Hasil Diagnosa:\n"
            for penyakit, info in hasil_diagnosa.items():
                peluang = info['Peluang']
                gejala_user = info['Gejala penyakit yang diinputkan user']
                total_gejala = info['Total gejala']

                response += f"Peluang terkena {penyakit}: {peluang}\n"
                response += f"Gejala penyakit {penyakit} yang diinputkan user: {gejala_user}\n"
                response += f"Total gejala {penyakit}: {total_gejala}\n\n"

            # bot.reply_to(message, response)
            print(message, response)
            response = tampilkan_hasil(hasil_diagnosa)
            bot.reply_to(message, response)

            gejala_tanya = ""
            penyakit_terdeteksi = ""
            gejala_sebelumnya = []

bot.polling()