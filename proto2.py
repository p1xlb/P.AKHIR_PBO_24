import os
from abc import ABC, abstractmethod
from getpass import getpass
import mysql.connector # python -m pip install mysql-connector-python
import prettytable
import datetime
from datetime import datetime
import random
import time

# koneksi ke database dbkeuangan
db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database= "dbkeuangan",
  
)
kota_list = ["Kab. Paser","Kab. Kutai Kartanegara","Kab. Berau","Kab. Kutai Barat","Kab. Kutai Timur","Kab. Penajam Paser Utara","Kab. Mahakam Ulu","Kota Balikpapan","Kota Samarinda","Kota Bontang"]

alokasi_list= ["pendidikan","kesehatan", "infrastruktur", "teknologi"]
max_tahun = datetime.now().year


def generate_nip(tahun_lahir, bulan_lahir):
    kode_instansi = "55"  
    kode_bulan = str(bulan_lahir).zfill(2)  # Isi 0 di depan jika bulan < 10
    kode_tahun = str(tahun_lahir)[2:]  # Ambil 2 digit terakhir tahun
    nomor_urut = str(random.randint(1, 9999)).zfill(4)  # Isi 0 di depan jika nomor urut < 1000

    nip = f"{kode_instansi}{kode_bulan}{kode_tahun}{nomor_urut}"

    return nip

def cls():
    # os.system("clear")
    os.system("cls")


class LaporanKeuangan(ABC):
    def __init__(self, tahun, total, kota):
        self.tahun = tahun
        self.total = total
        self.kota = kota
        self.daftar = []

    def tambah_item(self, item):
        self.daftar.append(item)

    def hapus_item(self, item):
        self.daftar.remove(item)

    @abstractmethod
    def hitung_total(self):
        pass


class ItemLaporan:
    def __init__(self,id, nama, jumlah, tahun, deskripsi, status):
        self.id = id
        self.nama = nama
        self.jumlah = jumlah
        self.tahun = tahun
        self.deskripsi = deskripsi
        self.status = status

    def getTahun(self):
        return self.tahun

class Anggaran(LaporanKeuangan):
    def __init__(self, tahun, total, kota):
        super().__init__(tahun, total, kota)

    def hitung_total(self):
        total = sum(item.jumlah for item in self.daftar)
        return total

    def ubah_total_anggaran(self, kota, tahun, total_baru):
        if kota in self.anggaran_kota:
            anggaran = self.anggaran_kota[kota]
            if anggaran.tahun == tahun:
                mycursor = db.cursor()
                sql = "UPDATE tb_anggaran SET total = %s WHERE kota = %s AND tahun = %s"
                val = (total_baru, kota, tahun)
                mycursor.execute(sql, val)
                db.commit()
                anggaran.total = total_baru
                print(f"Total anggaran untuk kota {kota} pada tahun {tahun} telah diubah menjadi {total_baru}.")
            else:
                print(f"Anggaran untuk kota {kota} pada tahun {tahun} tidak ditemukan.")
        else:
            print(f"Anggaran untuk kota {kota} pada tahun {tahun} belum dibuat.")

    def setujui_anggaran(self, kota, tahun):
        try:
            mycursor = db.cursor()
            # Ambil total anggaran dari tabel tb_anggaran
            sql_total = "SELECT total FROM tb_anggaran WHERE kota = %s AND tahun = %s"
            params_total = (kota, tahun)
            mycursor.execute(sql_total, params_total)
            result_total = mycursor.fetchone()

            if result_total:
                total_anggaran = result_total[0]
                total_anggaran_formatted = "{:,.2f}".format(total_anggaran)

                # Ambil alokasi anggaran dari tabel tb_alokasi
                sql_alokasi = "SELECT tb_alokasi.id, tb_alokasi.alokasi, tb_alokasi.jumlah, tb_alokasi.deskripsi, tb_alokasi.status, tb_alokasi.catatan " \
                               "FROM tb_alokasi " \
                               "JOIN tb_anggaran ON tb_alokasi.kota = tb_anggaran.kota AND tb_alokasi.tahun = tb_anggaran.tahun " \
                               "WHERE tb_alokasi.kota = %s AND tb_alokasi.tahun = %s"
                params_alokasi = (kota, tahun)
                mycursor.execute(sql_alokasi, params_alokasi)
                result = mycursor.fetchall()

                if result:
                    print(f"== Alokasi Anggaran {kota} - {tahun} ==")
                    print(f"Total Anggaran: Rp {total_anggaran_formatted}")
                    table = prettytable.PrettyTable()
                    table.field_names = ["ID", "Alokasi", "Jumlah", "Deskripsi", "Status", "Catatan"]
                    total_alokasi = 0

                    for row in result:
                        jumlah_formatted = "{:,.2f}".format(row[2])
                        table.add_row([row[0], row[1], jumlah_formatted, row[3], row[4], row[5]])
                        total_alokasi += row[2]

                    print(table)

                    # Periksa apakah over atau under budget
                    selisih = total_alokasi - total_anggaran
                    if selisih > 0:
                        total_alokasi_formatted = "{:,.2f}".format(total_alokasi)
                        print(f"Total alokasi anggaran Rp {total_alokasi_formatted} melebihi total anggaran Rp {total_anggaran_formatted}. Overbudget sebesar Rp {selisih:,.2f}!")
                    elif selisih < 0:
                        total_alokasi_formatted = "{:,.2f}".format(total_alokasi)
                        print(f"Total alokasi anggaran Rp {total_alokasi_formatted} kurang dari total anggaran Rp {total_anggaran_formatted}. Underbudget sebesar Rp {-selisih:,.2f}!")
                    else:
                        print("Total alokasi anggaran sesuai dengan total anggaran.")

                    id_alokasi = input("Masukkan ID alokasi yang ingin disetujui: ")

                    if id_alokasi.isdigit():
                        found = False
                        for row in result:
                            if str(row[0]) == id_alokasi:
                                found = True
                                konfirmasi = input(f"Konfirmasi anggaran (y/n/r (revisi)): ")
                                status = ""
                                catatan = ""
                                if konfirmasi.lower() == "y":
                                    status = "setuju"
                                elif konfirmasi.lower() == "n":
                                    status = "tidak setuju"
                                elif konfirmasi.lower() == "r":
                                    status = "revisi"
                                    catatan = input("Masukkan catatan: ")

                                sql_update = "UPDATE tb_alokasi SET status = %s, catatan = %s WHERE tb_alokasi.id = %s"
                                val = (status, catatan, id_alokasi)
                                mycursor.execute(sql_update, val)
                                db.commit()

                                print(f"Alokasi anggaran dengan ID {id_alokasi} untuk kota {kota} pada tahun {tahun} telah dikonfirmasi.")
                                break
                            
                        if not found:
                            print(f"ID alokasi {id_alokasi} tidak ditemukan.")
                    else:
                        print("ID alokasi tidak valid.")

                else:
                    print(f"Anggaran untuk kota {kota} pada tahun {tahun} tidak ditemukan.")
            else:
                print(f"Anggaran untuk kota {kota} pada tahun {tahun} tidak ditemukan.")
        except Exception as e:
            print(f"Terjadi kesalahan: {e}")

    def lihat_anggaran(self, kota, tahun):
        try:
            mycursor = db.cursor()
            # Ambil total anggaran dari tabel tb_anggaran
            sql_total = "SELECT total FROM tb_anggaran WHERE kota = %s AND tahun = %s"
            params_total = (kota, tahun)
            mycursor.execute(sql_total, params_total)
            result_total = mycursor.fetchone()
    
            if result_total:
                total_anggaran = result_total[0]
                total_anggaran_formatted = "{:,.2f}".format(total_anggaran)
    
                # Ambil alokasi anggaran dari tabel tb_alokasi
                sql_alokasi = "SELECT tb_alokasi.alokasi, tb_alokasi.jumlah, tb_alokasi.deskripsi, tb_alokasi.status, tb_alokasi.catatan " \
                    "FROM tb_alokasi " \
                    "JOIN tb_anggaran ON tb_alokasi.kota = tb_anggaran.kota AND tb_alokasi.tahun = tb_anggaran.tahun " \
                    "WHERE tb_alokasi.kota = %s AND tb_alokasi.tahun = %s"
                params_alokasi = (kota, tahun)
                mycursor.execute(sql_alokasi, params_alokasi)
                result_alokasi = mycursor.fetchall()
    
                if result_alokasi:
                    print(f"== Alokasi Anggaran {kota} - {tahun} ==")
                    table = prettytable.PrettyTable()
                    table.field_names = ["Alokasi", "Jumlah", "Deskripsi", "Status", "Catatan"]
                    total_alokasi = 0
    
                    for row in result_alokasi:
                        jumlah_formatted = "{:,.2f}".format(row[1])
                        table.add_row([row[0], jumlah_formatted, row[2], row[3], row[4]])
                        total_alokasi += row[1]
    
                    print(table)
    
                    # Periksa apakah over atau under budget
                    selisih = total_alokasi - total_anggaran
                    if selisih > 0:
                        total_alokasi_formatted = "{:,.2f}".format(total_alokasi)
                        print(f"Total alokasi anggaran Rp {total_alokasi_formatted} melebihi total anggaran Rp {total_anggaran_formatted}. Overbudget sebesar Rp {selisih:,.2f}!")
                    elif selisih < 0:
                        total_alokasi_formatted = "{:,.2f}".format(total_alokasi)
                        print(f"Total alokasi anggaran Rp {total_alokasi_formatted} kurang dari total anggaran Rp {total_anggaran_formatted}. Underbudget sebesar Rp {-selisih:,.2f}!")
                    else:
                        print("Total alokasi anggaran sesuai dengan total anggaran.")
                else:
                    print(f"Anggaran untuk kota {kota} pada tahun {tahun} tidak ditemukan.")
            else:
                print(f"Anggaran untuk kota {kota} pada tahun {tahun} tidak ditemukan.")
        except Exception as e:
            print(f"Terjadi kesalahan: {e}")

class Pendapatan(LaporanKeuangan):
    def __init__(self, tahun, total, kota):
        super().__init__(tahun, total, kota)

    def hitung_total(self):
        total = sum(item.jumlah for item in self.daftar)
        return total

    def cetak_laporan(self):
        print(f"Laporan Pendapatan Tahun {self.tahun}")
        print(f"Kota: {self.kota}")
        print(f"Total Pendapatan: Rp {self.total:,.2f}")
        print("Daftar Pendapatan:")
        for item in self.daftar:
            print(f"- {item.nama}: Rp {item.jumlah:,.2f}")
        total_pendpt = "{:,.2f}".format(self.hitung_total)
        print(f"Total Pendapatan: Rp {total_pendpt}")

    def insertPendapatanToList(self):
        self.anggaran_kota.clear()
        mycursor = db.cursor()

        mycursor.execute("SELECT * FROM tb_pendapatan")

        myresult = mycursor.fetchall()

        for x in myresult:

            kota = x[2]
            total = x[3]
            tahun = x[4]
            pendapatan = Pendapatan(tahun, total, kota)
            self.pendapatan_kota[kota] = pendapatan
    
    def tambah_pendapatan(self, kota, tahun, total, nama, deskripsi):
        if kota in self.pendapatan_kota and tahun == self.pendapatan_kota[kota].tahun:
            print(f"Pendapatan untuk kota {kota} pada tahun {tahun} sudah ada.")
        else :
            mycursor = db.cursor()

            sql = "INSERT INTO tb_pendapatan (kota, tahun, total, nama_pendapatan, deskripsi) VALUES (%s, %s, %s, %s, %s)"
            val = (kota,tahun,total, nama, deskripsi)
            mycursor.execute(sql, val)

            db.commit()
            print(f"Pendapatan untuk kota {kota} pada tahun {tahun} telah dibuat.")
        
    def lihat_pendapatan(self, kota, tahun):
        mycursor = db.cursor()
        sql = "SELECT nama_pendapatan, kota, total, tahun, deskripsi FROM tb_pendapatan WHERE kota = %s AND tahun = %s"
        params = (kota, tahun)
        mycursor.execute(sql, params)
        res = mycursor.fetchall()

        if res:
            table = prettytable.PrettyTable()
            table.field_names = ["Nama pendapatan", "Kota", "Total", "Tahun", "Deskripsi"]

            total_pendapatan = 0

            for row in res:   
                table.add_row(row)
                total_pendapatan += row[2]  # Menjumlahkan kolom 'total'

            print(table)
            total_pendapatan_formatted = "{:,.2f}".format(total_pendapatan)
            print(f"Total Pendapatan: Rp {total_pendapatan_formatted}")
        else:
            print(f"Laporan pendapatan untuk kota {kota} pada tahun {tahun} tidak ditemukan.")

class user:
    def __init__(self, nama, username, password, role):
        self.nama = nama
        self.username = username
        self.password = password
        self.role = role

class SuperUser(user):
    def __init__(self, nama, username, password, role):
        super().__init__(nama, username, password, role)

    def lihat_akun(self):
        mycursor = db.cursor()
                
        mycursor.execute("SELECT nama, username, password ,role FROM tb_user WHERE NOT role = %s", ("super",))

        result = mycursor.fetchall()
        
        table = prettytable.PrettyTable()
        table.field_names = ["Nama", "Username", "Password", "Role"]
        if result :

            for row in result:
                table.add_row(row)

            print(table)
        else :
            print("tidak ada data!")
            return


    def tambah_akun(self, choice):
        while True:
            try:
                if choice == "1":
                    print("Buat Akun Kepala pegawai")
                    nama1 = input("Nama :")
                    username1 = input("Username :")
                    password1 = input("Password :")
                    check_username = checkUsername(username1)
                    if check_username:
                        print("username telah dipakai!")
                        continue
                    mycursor = db.cursor()
                    mycursor.execute("INSERT INTO tb_user (nama, username, password , role) VALUES (%s, %s, %s, %s)", (nama1,username1, password1, "admin"))

                    db.commit()
                    print("akun berhasil dibuat")
                    return

                elif choice == "2":
                    
                    print("Buat Akun Pegawai")
                    nama = input("Nama :")
                    username= input("Username :")
                    check_username = checkUsername(username)
                    if check_username:
                        print("username telah dipakai!")
                        continue

                    tahun_lahir = input("Masukkan tahun lahir (YYYY): ")
                    bulan_lahir = input("Masukkan bulan lahir (MM) : ")

                    if not tahun_lahir.isdigit() or len(tahun_lahir) != 4:
                        print("Tahun lahir harus berupa angka 4 digit!")
                        continue
                    if not bulan_lahir.isdigit() or len(bulan_lahir) != 2 or int(bulan_lahir) < 1 or int(bulan_lahir) > 12:
                        print("Bulan lahir harus berupa angka 2 digit antara 1 dan 12!")
                        continue
                    
                    nip = generate_nip(tahun_lahir, bulan_lahir)

                    while True :
                        print("\n\nAkun pegawai anda")
                        print("nama :" + nama)
                        print("username :" + username)
                        print("NIP :" + nip)
                        
                        confrm = input("apakah anda ingin melanjutkan (y/n) :")
                        
                        if confrm.lower() == "y":
                            
                            mycursor = db.cursor()
                            mycursor.execute("INSERT INTO tb_user (nama, username, password , role) VALUES (%s, %s, %s, %s)", (nama,username, nip, "user"))

                            db.commit()

                            print("akun berhasil dibuat")
                            return
                        elif confrm.lower() == "n":
                            print("akun gagal disimpan")
                            print("kembali ke menu.....")
                            
                            return

                        else :
                            print("input tidak valid!")

            except Exception as e:
                print("terjadi kesalahan : ", e)

class Pegawai(user):
    def __init__(self, nama, username, password, role):
        super(Pegawai, self).__init__(nama,username,password, role)

        self.anggaran_kota = {}
        self.pendapatan_kota = {}

    def insertAnggaranToArr(self): # retrive data dari db trus add ke dict
        self.anggaran_kota.clear()
        mycursor = db.cursor()

        mycursor.execute("SELECT * FROM tb_anggaran")

        myresult = mycursor.fetchall()

        for x in myresult:
            kota = x[1]
            tahun = x[2]
            total = x[3]
            anggaran = Anggaran(tahun, total, kota)
            self.anggaran_kota[kota] = anggaran
            # print(self.anggaran_kota)

    def buat_anggaran(self, kota, tahun, total):
        if kota in self.anggaran_kota:
            print(f"Anggaran untuk kota {kota} pada tahun {tahun} sudah ada.")
        else:
            anggaran = Anggaran(tahun, total, kota)
            self.anggaran_kota[kota] = anggaran

            mycursor = db.cursor()

            sql = "INSERT INTO tb_anggaran (kota, tahun, total) VALUES (%s, %s, %s)"
            val = (kota,tahun,total)
            mycursor.execute(sql, val)

            db.commit()

            print(f"Anggaran untuk kota {kota} pada tahun {tahun} telah dibuat.")


    def tambah_alokasi_anggaran(self, kota, tahun, nama, jumlah, deskripsi):
        if kota in self.anggaran_kota:
            anggaran = self.anggaran_kota[kota]
            # print(anggaran.tahun,tahun)
            if anggaran.tahun == tahun:
                # item = ItemLaporan(nama, jumlah, deskripsi)
                # anggaran.tambah_item(item)
                mycursor = db.cursor()

                sql = "INSERT INTO tb_alokasi (alokasi, kota, tahun, jumlah, deskripsi, status) VALUES (%s, %s, %s,%s, %s, %s)"
                val = (nama,kota,tahun,jumlah,deskripsi, "pending")

                mycursor.execute(sql, val)

                db.commit()


                print(f"Alokasi anggaran '{nama}' telah ditambahkan ke anggaran {kota} tahun {tahun}.")
            else:
                print(f"Anggaran untuk kota {kota} pada tahun {tahun} tidak ditemukan.")
        else:
            print(f"Anggaran untuk kota {kota} pada tahun {tahun} belum dibuat.")

    def ubah_total_anggaran(self, kota, total_baru):
        tahun_sekarang = datetime.now().year
        if kota in self.anggaran_kota:
            anggaran = self.anggaran_kota[kota]
            if anggaran.tahun == tahun_sekarang:
                mycursor = db.cursor()
                sql = "UPDATE tb_anggaran SET total = %s WHERE kota = %s AND tahun = %s"
                val = (total_baru, kota, tahun_sekarang)
                mycursor.execute(sql, val)
                db.commit()
                anggaran.total = total_baru
                total_baru_formatted = "{:,.2f}".format(total_baru)

                print(f"Total anggaran untuk kota {kota} pada tahun {tahun_sekarang} telah diubah menjadi {total_baru_formatted}.")
            else:
                print(f"Anggaran untuk kota {kota} pada tahun {tahun_sekarang} tidak ditemukan.")
        else:
            print(f"Anggaran untuk kota {kota} pada tahun {tahun_sekarang} belum dibuat.")

    def insertPendapatanToList(self):
        Pendapatan.insertPendapatanToList(self)

    def tambah_pendapatan(self, kota, tahun, total, nama, deskripsi):
        Pendapatan.tambah_pendapatan(self, kota, tahun, total, nama,deskripsi)      
    
    def lihat_pendapatan(self, kota, tahun):
        Pendapatan.lihat_pendapatan(self, kota, tahun)

    def hitung_alokasi_revisi(self):
        try:
            mycursor = db.cursor()
            sql = "SELECT COUNT(*) FROM tb_alokasi WHERE status = 'revisi'"
            mycursor.execute(sql)
            result = mycursor.fetchone()
            jumlah_revisi = result[0]
            return jumlah_revisi
        except Exception as e:
            print(f"Terjadi kesalahan: {e}")
            return 0

    def revisi_alokasi(self):
        try:
            mycursor = db.cursor()
            sql = "SELECT id, alokasi, kota, tahun, jumlah, deskripsi, catatan FROM tb_alokasi WHERE status = 'revisi'"
            mycursor.execute(sql)
            result = mycursor.fetchall()

            if result:
                print("Daftar Alokasi yang Perlu Direvisi:")
                table = prettytable.PrettyTable()
                table.field_names = ["ID", "Alokasi", "Kota", "Tahun", "Jumlah", "Deskripsi", "Catatan"]

                for row in result:
                    table.add_row(row)

                print(table)

                id_alokasi = input("Masukkan ID alokasi yang ingin direvisi: ")

                if id_alokasi.isdigit():
                    for row in result:
                        if str(row[0]) == id_alokasi:
                            alokasi = row[1]
                            kota = row[2]
                            tahun = row[3]
                            jumlah = int(input(f"Masukkan jumlah revisi untuk alokasi '{alokasi}': "))
                            deskripsi = input(f"Masukkan deskripsi revisi untuk alokasi '{alokasi}': ")

                            sql_update = "UPDATE tb_alokasi SET jumlah = %s, deskripsi = %s, status = 'pending' WHERE id = %s"
                            val = (jumlah, deskripsi, id_alokasi)
                            mycursor.execute(sql_update, val)
                            db.commit()

                            print(f"Alokasi dengan ID {id_alokasi} telah direvisi.")
                            break
                    else:
                        print(f"ID alokasi {id_alokasi} tidak ditemukan.")
                else:
                    print("ID alokasi tidak valid.")
            else:
                print("Tidak ada alokasi yang perlu direvisi.")
        except Exception as e:
            print(f"Terjadi kesalahan: {e}")
            
def checkUsername(username):
    if username != "":
        sql = db.cursor()
        sql.execute("SELECT * FROM tb_user WHERE username = %s", (username,))
        
        res = sql.fetchone()

        if res :return True
        else: return False

class Kepala(user):

    def __init__(self, nama, username, password, role):
        super(Kepala, self).__init__(nama,username,password, role)
        self.alokasi_anggaran = {}
        self.daftar_pendapatan = {}

    def insertAnggaranToArray(self):
        self.alokasi_anggaran.clear()
        mycursor = db.cursor()

        mycursor.execute("SELECT * FROM tb_alokasi")
        myresult = mycursor.fetchall()

        for x in myresult:
            id = x[0]
            nama_alokasi = x[1]
            kota = x[2]
            tahun = x[3]
            jumlah = x[4]
            deskripsi = x[5]
            status = x[6]

            item = ItemLaporan(id,nama_alokasi, jumlah,tahun, deskripsi, status)

            self.alokasi_anggaran[kota] = item
            # print(self.alokasi_anggaran)
        return

    def lihat_pendapatan(self, kota, tahun):
        Pendapatan.lihat_pendapatan(self, kota, tahun)
        
def login():
    max_attempts = 3
    attempts = 0

    while attempts < max_attempts:
        cls()
        print("Selamat datang di Sistem Pengelolaan Anggaran dan Pendapatan")
        username = input("Masukkan username: ")
        password = getpass("Masukkan password: ")

        cursor = db.cursor()
        cursor.execute("SELECT * FROM tb_user WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()

        if user:
            if user[4] == "admin":
                kepala_pegawai = Kepala(user[1], user[2], user[3], user[4])
             
                cls()
                print(f"Selamat datang, {kepala_pegawai.nama} (Kepala Pegawai)")
                return kepala_pegawai
            elif user[4] == "super":
                admin = SuperUser(user[1], user[2], user[3], user[4])
                print(f"Selamat datang, {admin.nama} (super user)")
                return admin
            
            else:
                pegawai = Pegawai(user[1], user[2], user[3], user[4])
             
                cls()
                print(f"Selamat datang, {pegawai.nama} (Pegawai)")
                return pegawai
            
        else:
            attempts += 1 
            print("Login gagal. Username atau password salah.")
            print("kesempatan login:", attempts, "/", max_attempts)
            if attempts == max_attempts:
                print("\nAnda telah mencapai batas maksimum percobaan login.")
                break
            time.sleep(1)

    print("Keluar dari program...")
    exit()

def lihatKota():
    print("=============================")
    print("| No \t | Kota  \t\t|")
    print("=============================")
    for i, value in enumerate(kota_list):

        print(f"|{i+1}| {value}")
    print("=============================")

def lihatAlokasi():
    print("=============================")
    print("| No \t | Alokasi  \t\t|")
    print("=============================")
    for i, value in enumerate(alokasi_list):

        print(f"|{i+1}| {value}")
    print("=============================")

def menu_pegawai(pegawai):
    global kota_list, alokasi_list
    tahun = datetime.now().year
    pegawai.insertAnggaranToArr()
    jumlah_revisi = pegawai.hitung_alokasi_revisi()

    if jumlah_revisi > 0:
        print(f"Perhatian! Terdapat {jumlah_revisi} alokasi yang perlu direvisi.")
    time.sleep(2)

    while True:
        print("\nMenu Pegawai")
        print("1. Manajemen Anggaran")
        print("2. Manajemen Pendapatan")
        print("0. Keluar")

        pilihan = input("Masukkan pilihan: ")

        if pilihan == "1":  # Anggaran
            print("\nMenu Anggaran")
            print("1. Buat Anggaran")
            print("2. Ubah Total Anggaran Tahun Ini")
            print("3. Lihat Anggaran")
            print("4. Tambah Alokasi Anggaran")
            print("5. Revisi Alokasi Anggaran")
            print("0. Kembali")

            pilihan_anggaran = input("Masukkan pilihan: ")

            if pilihan_anggaran == "1":
                kota= ""
                while True:
                    try:
                        lihatKota()
                        
                        kota_idx = int(input("pilih kota (0 = kembali): "))
                        if kota_idx == 0:
                            pass
                        if 0 < kota_idx <= len(kota_list):
                            print(kota_list[kota_idx - 1])
                            kota = kota_list[kota_idx - 1]
                            break
                        else:
                            print("pilih kota tidak valid!")

                    except Exception as e:
                        print("terdapat kesalahan :", e)
                        continue

                while True:
                    try:
                        total = int(input("Masukkan total anggaran: "))
                        if total <= 0 :
                            print("total anggaran tidak boleh kurang dari 0")
                            continue
                        elif total > 0 and total <= 1000 :
                            print("total anggaran harus lebih dari 1000")
                            continue
                        else :
                            break
                    except Exception as e:
                        print(e)  
                        continue
                pegawai.buat_anggaran(kota, tahun, total)
                input("tekan enter untuk melanjutkan.....")
                cls()

            elif pilihan_anggaran == "2":
                kota = ""
                while True:
                    try:
                        lihatKota()
                        kota_idx = int(input("Pilih kota (0 = kembali): "))
                        if kota_idx == 0:
                            break
                        if 0 < kota_idx <= len(kota_list):
                            kota = kota_list[kota_idx - 1]
                            break
                        else:
                            print("Pilih kota tidak valid!")
                    except Exception as e:
                        print("Terdapat kesalahan:", e)
                        continue

                if kota:
                    try:
                        total_baru = float(input("Masukkan total anggaran baru: "))
                        pegawai.ubah_total_anggaran(kota, total_baru)
                    except Exception as e:
                        print("Terdapat kesalahan:", e)

            elif pilihan_anggaran == "3":
                kota= ""
                while True:
                    try:
                        lihatKota()
                        
                        kota_idx = int(input("pilih kota (0 = kembali): "))
                        if kota_idx == 0:
                            pass
                        if 0 < kota_idx <= len(kota_list):
                            print(kota_list[kota_idx - 1])
                            kota = kota_list[kota_idx - 1]
                            break
                        else:
                            print("pilih kota tidak valid!")

                    except Exception as e:
                        print("terdapat kesalahan :", e)
                        continue

                # kota = input("Masukkan kota: ")
                while True:
                    try :
                        tahun = int(input("Masukkan tahun: "))

                        if not 2000 < tahun <= max_tahun:
                            print("tahun tidak valid!")
                            continue
                        else:
                            break
                    except Exception as e:
                        print("terjadi kesalahan :" ,e)
            
                anggaran = Anggaran(tahun, 0, kota)
                anggaran.lihat_anggaran(kota, tahun)
                input("tekan enter untuk melanjutkan.....")
                cls()

            elif pilihan_anggaran == "4":
                kota= ""
                while True:
                    try:
                        lihatKota()
                        
                        kota_idx = int(input("pilih kota (0 = kembali): "))
                        if kota_idx == 0:
                            pass
                        if 0 < kota_idx <= len(kota_list):
                            print(kota_list[kota_idx - 1])
                            kota = kota_list[kota_idx - 1]
                            break
                        else:
                            print("pilih kota tidak valid!")

                    except Exception as e:
                        print("terdapat kesalahan :", e)
                        continue
                    
                # tahun = int(input("Masukkan tahun: "))
                lihatAlokasi()
                alokasi_idx = int(input("pilih alokasi :"))
                nama = ""
                if 0 < alokasi_idx <= len(alokasi_list):
                    print(alokasi_list[alokasi_idx - 1])
                    nama = alokasi_list[alokasi_idx - 1]
                else:
                    print("pilih alokasi tidak valid!")
                # nama = input("Masukkan nama alokasi: ")

                while True:
                    try:
                        jumlah = float(input("Masukkan jumlah alokasi: "))
                        if jumlah <= 0 :
                            print("jumlah alokasi tidak boleh kurang dari 0")
                            continue
                        elif jumlah >0 and jumlah <= 1000:
                            print("jumlah alokasi harus lebih dari 1000")
                            continue
                        else :
                            break
                    except Exception as e:
                        print("terdapat kesalahan :", e)
                        continue

                deskripsi = input("Masukkan deskripsi alokasi: ")
                pegawai.tambah_alokasi_anggaran(kota, tahun, nama, jumlah, deskripsi)
                input("tekan enter untuk melanjutkan.....")
                cls()

            elif pilihan_anggaran == "5":
                pegawai.revisi_alokasi()
                input("tekan enter untuk melanjutkan.....")
                cls()

            elif pilihan_anggaran == "0":
                continue

            else:
                print("Pilihan tidak valid!")

        elif pilihan == "2":  # Pendapatan
            print("\nMenu Pendapatan")
            print("1. Tambah Pendapatan")
            print("2. Lihat Pendapatan")
            print("0. Kembali")

            pilihan_pendapatan = input("Masukkan pilihan: ")

            if pilihan_pendapatan == "1":
                try :
                    lihatKota()

                    kota_idx = int(input("pilih kota: "))
                    kota= ""
                    if 0 < kota_idx <= len(kota_list):
                        print(kota_list[kota_idx - 1])
                        kota = kota_list[kota_idx - 1]
                    else:
                        print("pilih kota tidak valid!")
                    # tahun = int(input("Masukkan tahun: "))

                    nama = input("Masukkan nama pendapatan: ")

                    while True:
                        try :
                            jumlah = float(input("Masukkan jumlah pendapatan: "))

                            if jumlah <= 0 :
                                print("jumlah pendapatan tidak boleh kurang dari 0 ")
                                continue
                            elif jumlah >0 and jumlah <= 1000:
                                print("jumlah pendapatan harus lebih dari 1000")
                                continue
                            else :
                                break
                        except Exception as e :
                            print("terdapat kesalahan :", e)
                            continue
                    deskripsi = input("Masukkan deskripsi pendapatan: ")
                except Exception as e :
                    print("terdapat kesalahan :" , e)

                pegawai.tambah_pendapatan(kota, tahun, jumlah, nama, deskripsi)
                input("tekan enter untuk melanjutkan.....")
                cls()

            elif pilihan_pendapatan == "2":
                lihatKota()
            
                kota_idx = int(input("pilih kota: "))
                kota= ""
                if 0 < kota_idx <= len(kota_list):
                    print(kota_list[kota_idx - 1])
                    kota = kota_list[kota_idx - 1]
                else:
                    print("pilih kota tidak valid!")

                while True:
                    try :
                        tahun = int(input("Masukkan tahun: "))

                        if not 2000 < tahun <= max_tahun:
                            print("tahun tidak valid!")
                            continue
                        else:
                            break
                    except Exception as e:
                        print("terjadi kesalahan :" ,e)
                
            
                pegawai.insertPendapatanToList()
                pegawai.lihat_pendapatan(kota, tahun)
                input("tekan enter untuk melanjutkan....")
            elif pilihan_pendapatan == "0":
                continue

            else:
                print("Pilihan tidak valid!")

        elif pilihan == "0":
            break
        else:
            print("Pilihan tidak valid!")

def menu_kepala(kepala):
    global kota_list
    time.sleep(1)
    
    while True:
        kepala.insertAnggaranToArray()

        print("\nMenu Kepala")
        print("1. Lihat Anggaran")
        print("2. Setujui Anggaran")
        print("3. Lihat Laporan Pendapatan")
        print("0. Keluar")

        pilihan = input("Masukkan pilihan: ")

        if pilihan == "1":
            kota= ""
            while True:
                    try:
                        lihatKota()
                        
                        kota_idx = int(input("pilih kota (0 = kembali): "))
                        if kota_idx == 0:
                            menu_kepala(kepala)
                        if 0 < kota_idx <= len(kota_list):
                            print(kota_list[kota_idx - 1])
                            kota = kota_list[kota_idx - 1]
                            break
                        else:
                            print("pilih kota tidak valid!")

                    except Exception as e:
                        print("terdapat kesalahan :", e)
                        continue
            while True:
                try :
                    tahun = int(input("Masukkan tahun: "))

                    if not 2000 < tahun <= max_tahun:
                        print("tahun tidak valid!")
                        continue
                    else:
                        break
                except Exception as e:
                    print("terjadi kesalahan :" ,e)
            
            
            anggaran = Anggaran(tahun, 0, kota)
            anggaran.lihat_anggaran(kota, tahun)
            input("tekan enter untuk melanjutkan.....")
            cls()

        elif pilihan == "2":
            kota= ""
            while True:
                try:
                    lihatKota()
                    
                    kota_idx = int(input("pilih kota (0 = kembali): "))
                    if kota_idx == 0:
                        menu_kepala(kepala)
                    if 0 < kota_idx <= len(kota_list):
                        print(kota_list[kota_idx - 1])
                        kota = kota_list[kota_idx - 1]
                        break
                    else:
                        print("pilih kota tidak valid!")

                except Exception as e:
                    print("terdapat kesalahan :", e)
                    continue

            while True:
                try :
                    tahun = int(input("Masukkan tahun: "))

                    if not 2000 < tahun <= max_tahun:
                        print("tahun tidak valid!")
                        continue
                    else:
                        break
                except Exception as e:
                    print("terjadi kesalahan :" ,e)
            
            
            anggaran = Anggaran(tahun, 0, kota)
            anggaran.setujui_anggaran(kota, tahun)
            input("tekan enter untuk melanjutkan.....")
            cls()

        elif pilihan == "3":
            kota= ""
            while True:
                try:
                    lihatKota()
                    
                    kota_idx = int(input("pilih kota (0 = kembali): "))
                    if kota_idx == 0:
                        menu_kepala(kepala)
                    if 0 < kota_idx <= len(kota_list):
                        print(kota_list[kota_idx - 1])
                        kota = kota_list[kota_idx - 1]
                        break
                    else:
                        print("pilih kota tidak valid!")

                except Exception as e:
                    print("terdapat kesalahan :", e)
                    continue

            while True:
                try :
                    tahun = int(input("Masukkan tahun: "))

                    if not 2000 < tahun <= max_tahun:
                        print("tahun tidak valid!")
                        continue
                    else:
                        break
                except Exception as e:
                    print("terjadi kesalahan :" ,e)
            
            
            kepala.lihat_pendapatan(kota, tahun)
            input("tekan enter untuk melanjutkan.....")
            cls()

        elif pilihan == "0":
            break
        else:
            print("Pilihan tidak valid!")

def menu_admin(admin):

    time.sleep(1)
    while True:
        try :
            print("\nMenu Admin")
            print("1. Lihat Akun")
            print("2. Tambah Akun ")
            print("0. keluar")
            choice = int(input("pilih :"))

            match(choice):
                case 0:
                    return
                case 1:
                    admin.lihat_akun()
                    input("tekan enter untuk melanjutkan.....")
                    cls()
                    
                case 2: 
                    while True:
                        print("1. tambah akun kepala")
                        print("2. tambah akun pegawai")
                        pilih = input("pilih : ")
                        if not pilih.isdigit():
                            print("pilihan harus berupa angka")
                        elif pilih != "1" and pilih != "2":
                            print("pilihan tidak ada")
                        else:
                            admin.tambah_akun(pilih)
                            input("tekan enter untuk melanjutkan.....")
                            cls()
                            break

                case _:
                    print("pilihan tidak ada")
                    
        except Exception as e:
            print("terjadi kesalahan :", e)
            input("tekan enter untuk melanjutkan.....")
            cls()
            continue

def main():
    while True:
        user = login()
        if user is not None:
            if isinstance(user, Pegawai):
                menu_pegawai(user)
            elif isinstance(user, Kepala):
                menu_kepala(user)
            elif isinstance(user, SuperUser):
                menu_admin(user)
        else:
            print("Keluar dari program...")
            break

if __name__ == "__main__":
    main()