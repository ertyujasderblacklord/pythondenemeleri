import bcrypt
import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import sqlite3

class BerberRandevuSistemi():
    def __init__(self):
        self.conn = sqlite3.connect('berber_randevu.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS kullanicilar (
                id INTEGER PRIMARY KEY,
                kullanici_adi TEXT,
                sifre_hash TEXT,
                salt TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS randevular (
                id INTEGER PRIMARY KEY,
                tarih_ve_saat TEXT,
                isim TEXT
            )
        ''')
        self.conn.commit()

    def kullanici_ekle(self, kullanici_adi, sifre):
        # Daha önce kullanıcı adı kullanılıyor mu kontrolü
        self.cursor.execute("SELECT kullanici_adi FROM kullanicilar WHERE kullanici_adi=?", (kullanici_adi,))
        existing_user = self.cursor.fetchone()
        if existing_user:
            messagebox.showerror("Hata", "Bu Kullanıcı Adı Zaten Kullanılıyor.")
            return
        
        # Kullanıcı adı ve şifre uzunluk kontrolü
        if len(kullanici_adi) < 6 or len(sifre) < 6:
            messagebox.showerror("Hata", "Kullanıcı adı ve şifre en az 6 karakter olmalıdır.")
            return

        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(sifre.encode('utf-8'), salt)

        self.cursor.execute("INSERT INTO kullanicilar (kullanici_adi, sifre_hash, salt) VALUES (?, ?, ?)", (kullanici_adi, password_hash.decode('utf-8'), salt.decode('utf-8')))
        self.conn.commit()
        messagebox.showinfo("Bilgi", "Kullanıcı başarıyla oluşturuldu!")

    def kullanici_giris(self, kullanici_adi, sifre):
        self.cursor.execute("SELECT sifre_hash, salt FROM kullanicilar WHERE kullanici_adi=?", (kullanici_adi,))
        user_data = self.cursor.fetchone()
        if user_data:
            saved_password_hash = user_data[0]
            saved_salt = user_data[1]

            input_password_hash = bcrypt.hashpw(sifre.encode("utf-8"), saved_salt.encode("utf-8"))

            if input_password_hash == saved_password_hash.encode("utf-8"):
                messagebox.showinfo("Bilgi", "Giriş Başarılı!\nRandevu İşlemlerine Devam Edebilirsiniz.")
                return True
            else:
                messagebox.showerror("Hata", "Şifre Hatalı.")
        else:
            messagebox.showerror("Hata", "Kullanıcı Adı Hatalı.")
        return False

    def randevu_al(self, tarih_ve_saat, isim):
        self.cursor.execute("INSERT INTO randevular (tarih_ve_saat, isim) VALUES (?, ?)", (tarih_ve_saat.strftime('%Y-%m-%d %H:%M'), isim))
        self.conn.commit()
        messagebox.showinfo("Bilgi", "Randevu başarıyla alındı!")

    def randevulari_goruntule(self):
        self.cursor.execute("SELECT tarih_ve_saat, isim FROM randevular")
        randevu_listesi = self.cursor.fetchall()
        formatted_randevular = "\n".join([f"Tarih: {randevu[0]}, İsim: {randevu[1]}" for randevu in randevu_listesi])
        messagebox.showinfo("Randevu Listesi", formatted_randevular)

berber_randevu_sistemi = BerberRandevuSistemi()

def kullanici_ekle_pencere():
    kullanici_adi = simpledialog.askstring("Kullanici Ekle", "Kullanici Adi:")
    sifre = simpledialog.askstring("Kullanici Ekle", "Sifre:")
    berber_randevu_sistemi.kullanici_ekle(kullanici_adi, sifre)

def kullanici_giris_pencere():
    kullanici_adi = simpledialog.askstring("Kullanici Giris", "Kullanici Adi:")
    sifre = simpledialog.askstring("Kullanici Giris", "Sifre:")
    berber_randevu_sistemi.kullanici_giris(kullanici_adi, sifre)

def randevu_al_pencere():
    tarih_str = simpledialog.askstring("Randevu Al", "Tarih (YYYY-AA-GG):")
    saat_str = simpledialog.askstring("Randevu Al", "Saat (HH:MM):")
    isim = simpledialog.askstring("Randevu Al", "Isim:")
    
    def tarih_ve_saat_kontrol(tarih_str, saat_str):
        try:
            tarih_parts = [int(part) for part in tarih_str.split('-')]
            saat_parts = [int(part) for part in saat_str.split(':')]

            tarih_obj = datetime.date(tarih_parts[0], tarih_parts[1], tarih_parts[2])
            saat_obj = datetime.time(saat_parts[0], saat_parts[1])

            tarih_ve_saat = datetime.datetime.combine(tarih_obj, saat_obj)
            
            if tarih_ve_saat < datetime.datetime.now():
                return False, None
            return True, tarih_ve_saat

        except ValueError:
            return False, None

    gecerli, tarih_ve_saat = tarih_ve_saat_kontrol(tarih_str, saat_str)

    if gecerli:
        berber_randevu_sistemi.randevu_al(tarih_ve_saat, isim)
    else: 
        messagebox.showerror("Hata", "Geçersiz Tarih Veya Saat Girişi!")

def ana_menu():
    ana_pencere = tk.Tk()
    ana_pencere.title("Berber Randevu Sistemi")

    kullanici_ekle_button = tk.Button(ana_pencere, text="Kullanici Ekle", command=kullanici_ekle_pencere)
    kullanici_ekle_button.pack(pady=10)

    kullanici_giris_button = tk.Button(ana_pencere, text="Giris Yap", command=kullanici_giris_pencere)
    kullanici_giris_button.pack(pady=10)

    randevu_al_button = tk.Button(ana_pencere, text="Randevu Al", command=randevu_al_pencere)
    randevu_al_button.pack(pady=10)

    randevulari_goruntule_button = tk.Button(ana_pencere, text="Randevulari Goruntule", command=berber_randevu_sistemi.randevulari_goruntule)
    randevulari_goruntule_button.pack(pady=10)

    ana_pencere.mainloop()

if __name__ == "__main__":
    ana_menu()
