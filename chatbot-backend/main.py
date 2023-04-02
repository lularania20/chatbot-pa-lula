from telebot import *
import re
import random

api = '5994491197:AAFEhWxSNOSGs8jOTEcZf4-hqnvRvKsjPdE'
bot = TeleBot(api)

# start
@bot.message_handler(commands=['start'])
def selamat_datang(message):
    bot.reply_to(message, 'Selamat Datang di Chatbot Layanan Konseling Politeknik Elektronika Negeri Surabaya')
    chatid = message.chat.id
    bot.send_message(chatid, 'Pilih Opsi Terkait Layanan Chatbot Konseling : \n'
                     '1. Sistem Diagnosis Kesehatan Mental \n'
                     '2. Sistem Informasi Kesehatan Mental')
    #bot.send_message(chatid, 'Terimakasih telah mengakses chatbot layanan konsultasi PENS. Apakah anda memiliki permasalahan, keluhan atau hal hal yang menjadi concern dalam masalah kesehatan mental anda? Silahkan sharing terkait apa yang sedang anda alami dan gejala yang anda rasakan.')

#chatbot
#answer = ['Terimakasih telah mengakses chatbot layanan konsultasi PENS. Apakah anda memiliki permasalahan, keluhan atau hal hal yang menjadi concern dalam masalah kesehatan mental anda? Silahkan sharing terkait apa yang sedang anda alami dan gejala yang anda rasakan.']
@bot.message_handler(content_types=['text'])
def chatbot(message):
     teks = message.text 
     #if re.findall('halo|hai', teks) :
     if re.findall('1|satu|Satu|Diagnosis|diagnosis', teks) :
         chatid = message.chat.id
         bot.send_message(chatid, 'Terimakasih telah mengakses chatbot layanan konsultasi PENS. Apakah anda memiliki permasalahan, keluhan atau hal hal yang menjadi concern dalam masalah kesehatan mental anda? Silahkan sharing terkait apa yang sedang anda alami dan gejala yang anda rasakan.') 
     elif re.findall('2|dua|Dua|Informasi|informasi', teks) :
         chatid = message.chat.id
         bot.send_message(chatid, '1. Anxiety \n'
                          '2. Depresi')
         if re.findall('1|satu|Satu|Anxiety|anxiety', teks) :
            chatid = message.chat.id
            bot.send_message(chatid, 'Anxiety adalah')
     else :
         chatid = message.chat.id
         bot.send_message(chatid, 'Nggak paham')

bot.polling(True)