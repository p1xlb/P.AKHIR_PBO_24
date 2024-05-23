import os

class Anggaran:
    def __init__(self, tahun_anggaran, total_anggaran, kota):
        self.tahun_anggaran = tahun_anggaran
        self.total_anggaran = total_anggaran
        self.kota = kota
        self.daftar_alokasi_anggaran = []

    def tambah_alokasi_anggaran(self, alokasi_anggaran):
        self.daftar_alokasi_anggaran.append(alokasi_anggaran)

    def hapus_alokasi_anggaran(self, alokasi_anggaran):
        self.daftar_alokasi_anggaran.remove(alokasi_anggaran)

    def hitung_total_anggaran(self):
        total = sum(alokasi.jumlah_anggaran for alokasi in self.daftar_alokasi_anggaran)
        return total

    def cek_status_anggaran(self):
        total_alokasi = self.hitung_total_anggaran()
        if total_alokasi > self.total_anggaran:
            selisih = total_alokasi - self.total_anggaran
            print(f"Anggaran overbudget sebesar Rp {selisih:,.2f}")
        elif total_alokasi < self.total_anggaran:
            selisih = self.total_anggaran - total_alokasi
            print(f"Anggaran underbudget sebesar Rp {selisih:,.2f}")
        else:
            print("Anggaran seimbang")

    def cetak_laporan_anggaran(self):
        print(f"Laporan Anggaran Pemerintah Provinsi Kalimantan Timur Tahun {self.tahun_anggaran}")
        print(f"Kota: {self.kota}")
        print(f"Total Anggaran: Rp {self.total_anggaran:,.2f}")
        print("Alokasi Anggaran:")
        for alokasi in self.daftar_alokasi_anggaran:
            print(f"- {alokasi.nama_alokasi}: Rp {alokasi.jumlah_anggaran:,.2f}")
        print(f"Total Alokasi Anggaran: Rp {self.hitung_total_anggaran():,.2f}")
        self.cek_status_anggaran()

    def simpan_anggaran_ke_file(self, nama_file):
        with open(nama_file, "w") as file:
            file.write(f"Tahun Anggaran: {self.tahun_anggaran}\n")
            file.write(f"Total Anggaran: {self.total_anggaran}\n")
            file.write(f"Kota: {self.kota}\n")
            file.write("Alokasi Anggaran:\n")
            for alokasi in self.daftar_alokasi_anggaran:
                file.write(f"{alokasi.nama_alokasi},{alokasi.jumlah_anggaran},{alokasi.deskripsi}\n")

    @classmethod
    def baca_anggaran_dari_file(cls, nama_file):
        if os.path.exists(nama_file):
            with open(nama_file, "r") as file:
                tahun_anggaran = int(file.readline().split(": ")[1])
                total_anggaran = float(file.readline().split(": ")[1])
                kota = file.readline().split(": ")[1].strip()
                anggaran = cls(tahun_anggaran, total_anggaran, kota)
                file.readline()  # Baca baris "Alokasi Anggaran:"
                for line in file:
                    nama_alokasi, jumlah_anggaran, deskripsi = line.strip().split(",")
                    alokasi = AlokasiAnggaran(nama_alokasi, float(jumlah_anggaran), deskripsi)
                    anggaran.tambah_alokasi_anggaran(alokasi)
            return anggaran
        else:
            print(f"File {nama_file} tidak ditemukan.")
            return None


class AlokasiAnggaran:
    def __init__(self, nama_alokasi, jumlah_anggaran, deskripsi):
        self.nama_alokasi = nama_alokasi
        self.jumlah_anggaran = jumlah_anggaran
        self.deskripsi = deskripsi


# Contoh penggunaan program
anggaran_2024_samarinda = Anggaran(2024, 5000000000000, "Samarinda")

alokasi_pendidikan = AlokasiAnggaran("Pendidikan", 1000000000000, "Untuk meningkatkan kualitas pendidikan")
alokasi_kesehatan = AlokasiAnggaran("Kesehatan", 800000000000, "Untuk meningkatkan fasilitas kesehatan")
alokasi_infrastruktur = AlokasiAnggaran("Infrastruktur", 1500000000000, "Untuk membangun infrastruktur baru")
alokasi_lainnya = AlokasiAnggaran("Lainnya", 2000000000000, "Untuk keperluan lainnya")

anggaran_2024_samarinda.tambah_alokasi_anggaran(alokasi_pendidikan)
anggaran_2024_samarinda.tambah_alokasi_anggaran(alokasi_kesehatan)
anggaran_2024_samarinda.tambah_alokasi_anggaran(alokasi_infrastruktur)
anggaran_2024_samarinda.tambah_alokasi_anggaran(alokasi_lainnya)

anggaran_2024_samarinda.cetak_laporan_anggaran()

# Simpan anggaran ke file
anggaran_2024_samarinda.simpan_anggaran_ke_file("anggaran_2024_samarinda.txt")

# Baca anggaran dari file
anggaran_dari_file = Anggaran.baca_anggaran_dari_file("anggaran_2024_samarinda.txt")
anggaran_dari_file.cetak_laporan_anggaran()