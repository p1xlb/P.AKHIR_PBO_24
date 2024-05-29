import os
from abc import ABC, abstractmethod
from getpass import getpass

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
        pass

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
    def __init__(self, nama, jumlah, deskripsi):
        self.nama = nama
        self.jumlah = jumlah
        self.deskripsi = deskripsi


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


class Pegawai:
    def __init__(self, nama, username, password):
        self.nama = nama
        self.username = username
        self.password = password
        self.anggaran_kota = {}
        self.pendapatan_kota = {}


    def buat_anggaran(self, kota, tahun, total):
        if kota in self.anggaran_kota:
            print(f"Anggaran untuk kota {kota} pada tahun {tahun} sudah ada.")
        else:
            anggaran = Anggaran(tahun, total, kota)
            self.anggaran_kota[kota] = anggaran
            print(f"Anggaran untuk kota {kota} pada tahun {tahun} telah dibuat.")

    def tambah_alokasi_anggaran(self, kota, tahun, nama, jumlah, deskripsi):
        if kota in self.anggaran_kota:
            anggaran = self.anggaran_kota[kota]
            if anggaran.tahun == tahun:
                item = ItemLaporan(nama, jumlah, deskripsi)
                anggaran.tambah_item(item)
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

    def tambah_pendapatan(self, kota, tahun, nama, jumlah, deskripsi):
        if kota in self.pendapatan_kota:
            pendapatan = self.pendapatan_kota[kota]
            if pendapatan.tahun == tahun:
                item = ItemLaporan(nama, jumlah, deskripsi)
                pendapatan.tambah_item(item)
                print(f"Pendapatan '{nama}' telah ditambahkan ke laporan pendapatan {kota} tahun {tahun}.")
            else:
                print(f"Laporan pendapatan untuk kota {kota} pada tahun {tahun} tidak ditemukan.")
        else:
            print(f"Laporan pendapatan untuk kota {kota} pada tahun {tahun} belum dibuat.")


class Kepala:
    def __init__(self, nama, username, password):
        self.nama = nama
        self.username = username
        self.password = password
        self.daftar_anggaran = {}
        self.daftar_pendapatan = {}

    def lihat_anggaran(self, kota, tahun):
        if kota in self.daftar_anggaran and tahun in self.daftar_anggaran[kota]:
            anggaran = self.daftar_anggaran[kota][tahun]
            anggaran.cetak_laporan()
        else:
            print(f"Anggaran untuk kota {kota} pada tahun {tahun} tidak ditemukan.")

    def setujui_anggaran(self, kota, tahun):
        if kota in self.daftar_anggaran and tahun in self.daftar_anggaran[kota]:
            anggaran = self.daftar_anggaran[kota][tahun]
            anggaran.cetak_laporan()
            konfirmasi = input(f"Apakah Anda ingin menyetujui anggaran ini? (y/n): ")
            if konfirmasi.lower() == "y":
                print(f"Anggaran untuk kota {kota} pada tahun {tahun} telah disetujui.")
            else:
                print(f"Anggaran untuk kota {kota} pada tahun {tahun} tidak disetujui.")
        else:
            print(f"Anggaran untuk kota {kota} pada tahun {tahun} tidak ditemukan.")

    def lihat_pendapatan(self, kota, tahun):
        if kota in self.daftar_pendapatan and tahun in self.daftar_pendapatan[kota]:
            pendapatan = self.daftar_pendapatan[kota][tahun]
            pendapatan.cetak_laporan()
        else:
            print(f"Laporan pendapatan untuk kota {kota} pada tahun {tahun} tidak ditemukan.")

    def terima_anggaran(self, anggaran):
        kota = anggaran.kota
        tahun = anggaran.tahun
        if kota not in self.daftar_anggaran:
            self.daftar_anggaran[kota] = {}
        self.daftar_anggaran[kota][tahun] = anggaran
        print(f"Anggaran untuk kota {kota} pada tahun {tahun} telah diterima.")

    def terima_pendapatan(self, pendapatan):
        kota = pendapatan.kota
        tahun = pendapatan.tahun
        if kota not in self.daftar_pendapatan:
            self.daftar_pendapatan[kota] = {}
        self.daftar_pendapatan[kota][tahun] = pendapatan
        print(f"Laporan pendapatan untuk kota {kota} pada tahun {tahun} telah diterima.")

def login():
    print("Selamat datang di Sistem Pengelolaan Anggaran dan Pendapatan")
    username = input("Masukkan username: ")
    password = getpass("Masukkan password: ")

    if username == "kepala" and password == "kepala123":
        kepala = Kepala("Kepala", username, password)
        return kepala
    elif username == "pegawai" and password == "pegawai123":
        pegawai = Pegawai("Pegawai", username, password)
        return pegawai
    else:
        print("Username atau password salah!")
        return None

def menu_pegawai(pegawai):
    while True:
        print("\nMenu Pegawai")
        print("1. Buat Anggaran")
        print("2. Tambah Alokasi Anggaran")
        print("3. Buat Laporan Pendapatan")
        print("4. Tambah Pendapatan")
        print("5. Keluar")

        pilihan = input("Masukkan pilihan: ")

        if pilihan == "1":
            kota = input("Masukkan kota: ")
            tahun = int(input("Masukkan tahun: "))
            total = float(input("Masukkan total anggaran: "))
            pegawai.buat_anggaran(kota, tahun, total)
        elif pilihan == "2":
            kota = input("Masukkan kota: ")
            tahun = int(input("Masukkan tahun: "))
            nama = input("Masukkan nama alokasi: ")
            jumlah = float(input("Masukkan jumlah alokasi: "))
            deskripsi = input("Masukkan deskripsi alokasi: ")
            pegawai.tambah_alokasi_anggaran(kota, tahun, nama, jumlah, deskripsi)
        elif pilihan == "3":
            kota = input("Masukkan kota: ")
            tahun = int(input("Masukkan tahun: "))
            total = float(input("Masukkan total pendapatan: "))
            pegawai.buat_laporan_pendapatan(kota, tahun, total)
        elif pilihan == "4":
            kota = input("Masukkan kota: ")
            tahun = int(input("Masukkan tahun: "))
            nama = input("Masukkan nama pendapatan: ")
            jumlah = float(input("Masukkan jumlah pendapatan: "))
            deskripsi = input("Masukkan deskripsi pendapatan: ")
            pegawai.tambah_pendapatan(kota, tahun, nama, jumlah, deskripsi)
        elif pilihan == "5":
            break
        else:
            print("Pilihan tidak valid!")

def menu_kepala(kepala):
    while True:
        print("\nMenu Kepala")
        print("1. Lihat Anggaran")
        print("2. Setujui Anggaran")
        print("3. Lihat Laporan Pendapatan")
        print("4. Keluar")

        pilihan = input("Masukkan pilihan: ")

        if pilihan == "1":
            kota = input("Masukkan kota: ")
            tahun = int(input("Masukkan tahun: "))
            kepala.lihat_anggaran(kota, tahun)
        elif pilihan == "2":
            kota = input("Masukkan kota: ")
            tahun = int(input("Masukkan tahun: "))
            kepala.setujui_anggaran(kota, tahun)
        elif pilihan == "3":
            kota = input("Masukkan kota: ")
            tahun = int(input("Masukkan tahun: "))
            kepala.lihat_pendapatan(kota, tahun)
        elif pilihan == "4":
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