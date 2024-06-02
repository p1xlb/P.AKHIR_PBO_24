import os
from abc import ABC, abstractmethod
from getpass import getpass
import mysql.connector # python -m pip install mysql-connector-python
import prettytable
import datetime
from datetime import datetime
import random


# koneksi ke database dbkeuangan
db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database= "dbkeuangan",
  
)
kota_list = ["Kab. Paser","Kab. Kutai Kartanegara","Kab. Berau","Kab. Kutai Barat","Kab. Kutai Timur","Kab. Penajam Paser Utara","Kab. Mahakam Ulu","Kota Balikpapan","Kota Samarinda","Kota Bontang"]

alokasi_list= ["pendidikan","kesehatan", "infrastruktur", "teknologi"]

def generate_nip(tahun_lahir, bulan_lahir):
    kode_instansi = "55"  
    kode_bulan = str(bulan_lahir).zfill(2)  # Isi 0 di depan jika bulan < 10
    kode_tahun = str(tahun_lahir)[2:]  # Ambil 2 digit terakhir tahun
    nomor_urut = str(random.randint(1, 9999)).zfill(4)  # Isi 0 di depan jika nomor urut < 1000

    nip = f"{kode_instansi}{kode_bulan}{kode_tahun}{nomor_urut}"

    return nip


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

    @abstractmethod
    def cetak_laporan(self):
        print(self.daftar)

    def simpan_ke_file(self, nama_file):
        with open(nama_file, "w") as file:
            file.write(f"Tahun: {self.tahun}\n")
            file.write(f"Total: {self.total}\n")
            file.write(f"Kota: {self.kota}\n")
            file.write("Daftar:\n")
            for item in self.daftar:
                file.write(f"{item.nama},{item.jumlah},{item.deskripsi}\n")

    @classmethod
    def baca_dari_file(cls, nama_file):
        if os.path.exists(nama_file):
            with open(nama_file, "r") as file:
                tahun = int(file.readline().split(": ")[1])
                total = float(file.readline().split(": ")[1])
                kota = file.readline().split(": ")[1].strip()
                laporan = cls(tahun, total, kota)
                file.readline()  # Baca baris "Daftar:"
                for line in file:
                    nama, jumlah, deskripsi = line.strip().split(",")
                    item = ItemLaporan(nama, float(jumlah), deskripsi)
                    laporan.tambah_item(item)
            return laporan
        else:
            print(f"File {nama_file} tidak ditemukan.")
            return None


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

    def cetak_laporan(self):
        print("p")

class Anggaran(LaporanKeuangan):
    def __init__(self, tahun, total, kota):
        super().__init__(tahun, total, kota)

    def hitung_total(self):
        total = sum(item.jumlah for item in self.daftar)
        return total

    def cetak_laporan(self):
        print(f"Laporan Anggaran Tahun {self.tahun}")
        print(f"Kota: {self.kota}")
        print(f"Total Anggaran: Rp {self.total:,.2f}")
        print("Alokasi Anggaran:")
        for item in self.daftar:
            print(f"- {item.nama}: Rp {item.jumlah:,.2f}")
        print(f"Total Alokasi Anggaran: Rp {self.hitung_total():,.2f}")
        self.cek_status_anggaran()

    def cek_status_anggaran(self):
        total_alokasi = self.hitung_total()
        if total_alokasi > self.total:
            selisih = total_alokasi - self.total
            print(f"Anggaran overbudget sebesar Rp {selisih:,.2f}")
        elif total_alokasi < self.total:
            selisih = self.total - total_alokasi
            print(f"Anggaran underbudget sebesar Rp {selisih:,.2f}")
        else:
            print("Anggaran seimbang")


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
        print(f"Total Pendapatan: Rp {self.hitung_total():,.2f}")


class user:

    def __init__(self, nama, username, password, role):
        self.nama = nama
        self.username = username
        self.password = password
        self.role = role


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


    def buat_laporan_pendapatan(self, kota, tahun, total):
        if kota in self.pendapatan_kota:
            print(f"Laporan pendapatan untuk kota {kota} pada tahun {tahun} sudah ada.")
        else:
            pendapatan = Pendapatan(tahun, total, kota)
            self.pendapatan_kota[kota] = pendapatan
            print(f"Laporan pendapatan untuk kota {kota} pada tahun {tahun} telah dibuat.")

    def tambah_pendapatan(self, kota, tahun, total, nama, deskripsi):
        if kota in self.pendapatan_kota and tahun == self.pendapatan_kota[kota].tahun:
            print(f"Pendapatan untuk kota {kota} pada tahun {tahun} sudah ada.")
        else :

            # pendapatan = Pendapatan(tahun, total, kota)
            # self.pendapatan_kota[kota] = pendapatan
            mycursor = db.cursor()

            sql = "INSERT INTO tb_pendapatan (kota, tahun, total, nama_pendapatan, deskripsi) VALUES (%s, %s, %s, %s, %s)"
            val = (kota,tahun,total, nama, deskripsi)
            mycursor.execute(sql, val)

            db.commit()
            print(f"Pendapatan untuk kota {kota} pada tahun {tahun} telah dibuat.")
        
            

        # if kota in self.pendapatan_kota:
        #     pendapatan = self.pendapatan_kota[kota]
        #     if pendapatan.tahun == tahun:
        #         item = ItemLaporan(nama, jumlah, deskripsi)
        #         pendapatan.tambah_item(item)
        #         print(f"Pendapatan '{nama}' telah ditambahkan ke laporan pendapatan {kota} tahun {tahun}.")
        #     else:
        #         print(f"Laporan pendapatan untuk kota {kota} pada tahun {tahun} tidak ditemukan.")
        # else:
        #     print(f"Laporan pendapatan untuk kota {kota} pada tahun {tahun} belum dibuat.")


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

    def lihat_anggaran(self, kota, tahun):
        try:
            mycursor = db.cursor()
            sql = "SELECT tb_alokasi.alokasi, tb_alokasi.jumlah, tb_alokasi.deskripsi, tb_alokasi.status, tb_alokasi.catatan " \
                  "FROM tb_alokasi " \
                  "JOIN tb_anggaran ON tb_alokasi.kota = tb_anggaran.kota AND tb_alokasi.tahun = tb_anggaran.tahun " \
                  "WHERE tb_alokasi.kota = %s AND tb_alokasi.tahun = %s"
            params = (kota, tahun)
            mycursor.execute(sql, params)
            result = mycursor.fetchall()

            if result:
                print(f"== Alokasi Anggaran {kota} - {tahun} ==")
                table = prettytable.PrettyTable()
                table.field_names = ["Alokasi", "Jumlah", "Deskripsi", "Status", "Catatan"]

                for row in result:
                    table.add_row(row)

                print(table)
            else:
                print(f"Anggaran untuk kota {kota} pada tahun {tahun} tidak ditemukan.")
        except Exception as e:
            print(f"Terjadi kesalahan: {e}")

    def setujui_anggaran(self, kota, tahun):
        try:
            mycursor = db.cursor()
            sql = "SELECT tb_alokasi.id, tb_alokasi.alokasi, tb_alokasi.jumlah, tb_alokasi.deskripsi, tb_alokasi.status, tb_alokasi.catatan " \
                  "FROM tb_alokasi " \
                  "JOIN tb_anggaran ON tb_alokasi.kota = tb_anggaran.kota AND tb_alokasi.tahun = tb_anggaran.tahun " \
                  "WHERE tb_alokasi.kota = %s AND tb_alokasi.tahun = %s"
            params = (kota, tahun)
            mycursor.execute(sql, params)
            result = mycursor.fetchall()
    
            if result:
                print(f"== Alokasi Anggaran {kota} - {tahun} ==")
                table = prettytable.PrettyTable()
                table.field_names = ["ID", "Alokasi", "Jumlah", "Deskripsi", "Status", "Catatan"]
    
                for row in result:
                    table.add_row(row)
    
                print(table)
    
                id_alokasi = input("Masukkan ID alokasi yang ingin disetujui: ")
    
                if id_alokasi.isdigit():
                    konfirmasi = input(f"Konfirmasi anggaran (y/n/r (revisi)): ")
                    status = ""
                    catatan = ""
                    if konfirmasi.lower() == "n":
                        status = "tidak setuju"
                    elif konfirmasi.lower() == "y":
                        status = "setuju"
                    elif konfirmasi.lower() == "r":
                        status = "revisi"
                        catatan = input("Masukkan catatan: ")
    
                    sql_update = "UPDATE tb_alokasi SET status = %s, catatan = %s WHERE tb_alokasi.id = %s"
                    val = (status, catatan, id_alokasi)
                    mycursor.execute(sql_update, val)
                    db.commit()
    
                    print(f"Alokasi anggaran dengan ID {id_alokasi} untuk kota {kota} pada tahun {tahun} telah dikonfirmasi.")
                else:
                    print("ID alokasi tidak valid.")
            else:
                print(f"Anggaran untuk kota {kota} pada tahun {tahun} tidak ditemukan.")
        except Exception as e:
            print(f"Terjadi kesalahan: {e}")

    def lihat_pendapatan(self, kota, tahun):
        
            # pendapatan = self.daftar_pendapatan[kota][tahun]
            # pendapatan.cetak_laporan()
            mycursor = db.cursor()

            sql = "SELECT * FROM tb_pendapatan WHERE kota = %s AND tahun = %s"
            params = (kota,tahun)

            mycursor.execute(sql, params)
            myresult = mycursor.fetchall()

            for x in myresult:
                # id = x[0]
                nama_pendapatan = x[1]
                kota = x[2]
                total = x[3]
                tahun = x[4]
                deskripsi = x[5]
                
                print(f'{nama_pendapatan} {kota} {total} {tahun} {deskripsi}')
              
            if len(myresult) == 0:
       
                print(f"Laporan pendapatan untuk kota {kota} pada tahun {tahun} tidak ditemukan.")

    # def terima_anggaran(self, anggaran):
    #     kota = anggaran.kota
    #     tahun = anggaran.tahun
    #     if kota not in self.daftar_anggaran:
    #         self.daftar_anggaran[kota] = {}
    #     self.daftar_anggaran[kota][tahun] = anggaran
    #     print(f"Anggaran untuk kota {kota} pada tahun {tahun} telah diterima.")

    # def terima_pendapatan(self, pendapatan):
    #     kota = pendapatan.kota
    #     tahun = pendapatan.tahun
    #     if kota not in self.daftar_pendapatan:
    #         self.daftar_pendapatan[kota] = {}
    #     self.daftar_pendapatan[kota][tahun] = pendapatan
    #     print(f"Laporan pendapatan untuk kota {kota} pada tahun {tahun} telah diterima.")

   
            
        

    def tambah_akun_pegawai(self):
        try:
            while True:
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
                        print("kembali ke menu.....")
                        
                        return

                    else :
                        print("input tidak valid!")



        except Exception as e:
            print(e)
            self.tambah_akun_pegawai()
            # return
        
        




def login():

    print("Selamat datang di Sistem Pengelolaan Anggaran dan Pendapatan")
    username = input("Masukkan username: ")
    password = getpass("Masukkan password: ")

    cursor = db.cursor()
    cursor.execute("SELECT * FROM tb_user WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()

    if user:
        if user[4] == "admin":
            kepala_pegawai = Kepala(user[1], user[2], user[3], user[4])
            
            print(f"Selamat datang, {kepala_pegawai.nama} (Kepala Pegawai)")
            return kepala_pegawai

        else:
            pegawai = Pegawai(user[1], user[2], user[3], user[4])
           
            print(f"Selamat datang, {pegawai.nama} (Pegawai)")
            return pegawai
        
    else:
        print("Login gagal. Username atau password salah.")

    # if username == "kepala" and password == "kepala123":
    #     kepala = Kepala("Kepala", username, password)
    #     return kepala
    # elif username == "pegawai" and password == "pegawai123":
    #     pegawai = Pegawai("Pegawai", username, password)
    #     return pegawai
    # else:
    #     print("Username atau password salah!")
    #     return None


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
    # print(tahun)
    pegawai.insertAnggaranToArr()
    while True:
        print("\nMenu Pegawai")
        print("1. Buat Anggaran")
        print("2. Tambah Alokasi Anggaran")
        # print("3. Buat Laporan Pendapatan") # membuat laporan terhadap data pendapatan yg sudah ada
        print("3. Tambah Pendapatan")
        print("0. Keluar")

        pilihan = input("Masukkan pilihan: ")

        if pilihan == "1":
            kota= ""

            while True:
                try:
                    lihatKota()
                    
                    kota_idx = int(input("pilih kota: "))
                    if 0 < kota_idx <= len(kota_list):
                        print(kota_list[kota_idx - 1])
                        kota = kota_list[kota_idx - 1]
                        break
                    else:
                        print("pilih kota tidak valid!")

                except Exception as e:
                    print(e)
                
            while True:
                try:
                    total = float(input("Masukkan total anggaran: "))

                except Exception as e:
                    print(e)  
                pegawai.buat_anggaran(kota, tahun, total)
                break

        elif pilihan == "2":
            lihatKota()
            
            kota_idx = int(input("pilih kota: "))
            kota= ""
            if 0 < kota_idx <= len(kota_list):
                print(kota_list[kota_idx - 1])
                kota = kota_list[kota_idx - 1]
            else:
                print("pilih kota tidak valid!")

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
            
            jumlah = float(input("Masukkan jumlah alokasi: "))
            deskripsi = input("Masukkan deskripsi alokasi: ")
            pegawai.tambah_alokasi_anggaran(kota, tahun, nama, jumlah, deskripsi)
        # elif pilihan == "3":
        #     lihatKota()
            
        #     kota_idx = int(input("pilih kota: "))
        #     kota= ""
        #     if 0 < kota_idx <= len(kota_list):
        #         print(kota_list[kota_idx - 1])
        #         kota = kota_list[kota_idx - 1]
        #     else:
        #         print("pilih kota tidak valid!")

        #     # tahun = int(input("Masukkan tahun: "))
        #     total = float(input("Masukkan total pendapatan: "))
        #     pegawai.buat_laporan_pendapatan(kota, tahun, total)

        elif pilihan == "3":
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
            jumlah = float(input("Masukkan jumlah pendapatan: "))
            deskripsi = input("Masukkan deskripsi pendapatan: ")
            pegawai.tambah_pendapatan(kota, tahun, jumlah, nama, deskripsi)
        elif pilihan == "0":
            break
        else:
            print("Pilihan tidak valid!")

def menu_kepala(kepala):
    global kota_list
    
    while True:
        kepala.insertAnggaranToArray()

        print("\nMenu Kepala")
        print("1. Lihat Anggaran")
        print("2. Setujui Anggaran")
        print("3. Lihat Laporan Pendapatan")
        print("4. Tambah akun pegawai")
        print("0. Keluar")

        pilihan = input("Masukkan pilihan: ")

        if pilihan == "1":
            lihatKota()
            
            kota_idx = int(input("pilih kota: "))
            kota= ""
            if 0 < kota_idx <= len(kota_list):
                print(kota_list[kota_idx - 1])
                kota = kota_list[kota_idx - 1]
            else:
                print("pilih kota tidak valid!")

            # kota = input("Masukkan kota: ")
            tahun = int(input("Masukkan tahun: "))
            kepala.lihat_anggaran(kota, tahun)
        elif pilihan == "2":
            lihatKota()
            
            kota_idx = int(input("pilih kota: "))
            kota= ""
            if 0 < kota_idx <= len(kota_list):
                print(kota_list[kota_idx - 1])
                kota = kota_list[kota_idx - 1]
            else:
                print("pilih kota tidak valid!")

            tahun = int(input("Masukkan tahun: "))
            kepala.lihat_anggaran(kota,tahun)
            kepala.setujui_anggaran(kota, tahun)
        elif pilihan == "3":
            lihatKota()
            
            kota_idx = int(input("pilih kota: "))
            kota= ""
            if 0 < kota_idx <= len(kota_list):
                print(kota_list[kota_idx - 1])
                kota = kota_list[kota_idx - 1]
            else:
                print("pilih kota tidak valid!")

            tahun = int(input("Masukkan tahun: "))
            kepala.lihat_pendapatan(kota, tahun)
        elif pilihan == "4":
            kepala.tambah_akun_pegawai()


        elif pilihan == "0":
            break
        else:
            print("Pilihan tidak valid!")

def main():
    while True:
        user = login()
        if user is not None:
            if isinstance(user, Pegawai):
                menu_pegawai(user)
            elif isinstance(user, Kepala):
                menu_kepala(user)
        else:
            print("Keluar dari program...")
            break

if __name__ == "__main__":
    main()