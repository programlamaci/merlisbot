import cv2 as cv
import numpy as np
import os
from time import time, sleep
from windowcapture import WindowCapture
from vision import Vision
import pyautogui
import tkinter as tk
from threading import Thread

# Change the working directory to the folder this script is in.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Global değişkenler
bot_calismakta = False  # Botun çalışıp çalışmadığını takip etmek için
tıklama_araligi = 12  # Başlangıç tıklama aralığı (saniye cinsinden)

# WindowCapture ve Vision sınıflarını başlat
wincap = WindowCapture('Merlis')
vision_limestone = Vision('albion_limestone.jpg')

# Botu çalıştıran fonksiyon
def bot_calistir():
    global bot_calismakta  # Global değişkeni kullanıyoruz
    global tıklama_araligi  # Tıklama aralığını global olarak kullanıyoruz
    bot_calismakta = True
    loop_time = time()

    while bot_calismakta:
        # Oyunun güncel görüntüsünü al
        screenshot = wincap.get_screenshot()

        # Güncel ekran görüntüsünde hedefleri bul
        points = vision_limestone.find(screenshot, 0.5, 'rectangles')

        # Eğer hedef bulunursa, ilk hedefe tıklayın
        if points:
            target_x, target_y = points[0]
            screen_x, screen_y = wincap.get_screen_position((target_x, target_y))
            pyautogui.moveTo(screen_x, screen_y)
            pyautogui.click()
            print(f"Tıklama yapıldı: ({screen_x}, {screen_y})")

            # Kullanıcı tarafından belirlenen tıklama aralığına göre bekle
            sleep(tıklama_araligi)
        else:
            print("Hedef bulunamadı, yeniden deneniyor.")

        # FPS'yi debug et
        print('FPS {}'.format(1 / (time() - loop_time)))
        loop_time = time()

        # 'q' tuşuna basıldığında çıkış yap
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            break

    print("Bot durdu.")

# Botu durduran fonksiyon
def bot_durdur():
    global bot_calismakta  # Global değişkeni kullanıyoruz
    bot_calismakta = False

# GUI arayüzü oluştur
def create_gui():
    global bot_calismakta  # Global değişkeni kullanıyoruz
    global tıklama_araligi  # Tıklama aralığını global olarak kullanıyoruz

    # Ana pencereyi oluştur
    pencere = tk.Tk()
    pencere.title("Bot Kontrolü")

    # Botun durumunu gösteren etiket
    durum_etiket = tk.Label(pencere, text="Bot durduruldu", font=("Arial", 12))
    durum_etiket.pack(pady=20)

    # Başlat/Durdur butonu
    def toggle_bot():
        global bot_calismakta  # Global değişkeni kullanıyoruz
        global tıklama_araligi  # Tıklama aralığını global olarak kullanıyoruz

        if bot_calismakta:
            # Botu durdur
            bot_durdur()
            buton.config(text="Başlat", bg="green")
            durum_etiket.config(text="Bot durduruldu")
        else:
            # Tıklama aralığını güncelle
            try:
                tıklama_araligi = float(tıklama_entry.get())  # Kullanıcının girdiği değeri al
                if tıklama_araligi <= 0:
                    raise ValueError("Tıklama aralığı pozitif bir sayı olmalı.")
            except ValueError as e:
                print(f"Hata: {e}")
                tıklama_araligi = 12  # Hata durumunda varsayılan değeri kullan
                tıklama_entry.delete(0, tk.END)
                tıklama_entry.insert(0, str(tıklama_araligi))

            # Botu başlat
            buton.config(text="Durdur", bg="red")
            durum_etiket.config(text="Bot çalışıyor")
            # Yeni bir thread'de botu çalıştır
            Thread(target=bot_calistir, daemon=True).start()

    buton = tk.Button(pencere, text="Başlat", command=toggle_bot, bg="green", width=15)
    buton.pack(pady=20)

    # Tıklama aralığını belirlemek için bir giriş alanı ekle
    tıklama_label = tk.Label(pencere, text="Tıklama aralığı (saniye):", font=("Arial", 10))
    tıklama_label.pack(pady=10)

    tıklama_entry = tk.Entry(pencere, font=("Arial", 10))
    tıklama_entry.insert(0, str(tıklama_araligi))  # Varsayılan tıklama aralığını göster
    tıklama_entry.pack(pady=5)

    # Pencereyi sürüklenebilir hale getirme
    def start_drag(event):
        pencere.x = event.x
        pencere.y = event.y

    def stop_drag(event):
        del pencere.x
        del pencere.y

    def drag_motion(event):
        delta_x = event.x - pencere.x
        delta_y = event.y - pencere.y
        x = pencere.winfo_x() + delta_x
        y = pencere.winfo_y() + delta_y
        pencere.geometry(f"+{x}+{y}")

    # Başlangıç sürükleme event'ini bağla
    pencere.bind("<ButtonPress-1>", start_drag)
    pencere.bind("<ButtonRelease-1>", stop_drag)
    pencere.bind("<B1-Motion>", drag_motion)

    # Pencereyi çalıştır
    pencere.mainloop()

# GUI'yi başlat
create_gui()
