from telebot import *
import re
import random
import telebot

api = '5994491197:AAFEhWxSNOSGs8jOTEcZf4-hqnvRvKsjPdE'
bot = TeleBot(api)


# Dataset gejala dan diagnosis
dataset = {
    'cemas ' : 'OCD',
    'capek': 'gangguan kecemasan',
    'gejala3': 'diagnosis3',
    # dan seterusnya
}

# Aturan-aturan berdasarkan gejala
aturan = {
    'cemas': ['OCD'],
    'gejala2': ['diagnosis2'],
    'gejala3': ['diagnosis3'],
    'cemas+ capek': ['gangguan kecemasan'],
    'gejala1+gejala3': ['diagnosis5'],
    # dan seterusnya
}

# start
@bot.message_handler(commands=['start'])
def selamat_datang(message):
    name = message.from_user.full_name
    bot.reply_to(message, f"Selamat Datang {name} di Chatbot Layanan Konseling Politeknik Elektronika Negeri Surabaya")
    markup = types.ReplyKeyboardMarkup()
    item1 = types.KeyboardButton('/start')
    item2 = types.KeyboardButton('/informasi')
    item3 = types.KeyboardButton('/diagnosis')
    item4 = types.KeyboardButton('/profile')
    markup.row(item1,item2)
    markup.row(item3, item4)
    
    # chatid = message.chat.id
    bot.reply_to(message, 'Pilih Opsi Terkait Layanan Chatbot Konseling', reply_markup=markup)
    #                  '1. Sistem Diagnosis Kesehatan Mental \n'
    #                  '2. Sistem Informasi Kesehatan Mental')
    #bot.send_message(chatid, 'Terimakasih telah mengakses chatbot layanan konsultasi PENS. Apakah anda memiliki permasalahan, keluhan atau hal hal yang menjadi concern dalam masalah kesehatan mental anda? Silahkan sharing terkait apa yang sedang anda alami dan gejala yang anda rasakan.')

# Fungsi untuk mencari diagnosis berdasarkan gejala
@bot.message_handler(commands=['diagnosis'])
def diagnosis(message) :
    bot.reply_to(message, 'Terimakasih telah mengakses chatbot layanan konsultasi PENS. Apakah anda memiliki permasalahan, keluhan atau hal hal yang menjadi concern dalam masalah kesehatan mental anda? Silahkan sharing terkait apa yang sedang anda alami dan gejala yang anda rasakan.')
def cari_diagnosis(gejala):
    diagnosis = []
    for k in aturan:
        if all(g in gejala for g in k.split('+')):
            diagnosis += aturan[k]
    return diagnosis

# Fungsi untuk menangani pesan dari pengguna
@bot.message_handler(func=lambda message: True)
def handle_message(message): 
    # Mendapatkan gejala dari pesan pengguna
    gejala = message.text.lower()
    # Mencari diagnosis berdasarkan gejala
    hasil_diagnosis = cari_diagnosis(gejala)
    # Memberikan respons ke pengguna
    if hasil_diagnosis:
        bot.reply_to(message, 'Diagnosis yang mungkin terjadi: {}'.format(', '.join(hasil_diagnosis)))
    else:
        bot.reply_to(message, 'Maaf, tidak dapat menemukan diagnosis yang sesuai dengan gejala yang diberikan.')

# Menjalankan bot
bot.polling()