-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Jun 04, 2024 at 01:17 AM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `dbkeuangan`
--

-- --------------------------------------------------------

--
-- Table structure for table `tb_alokasi`
--

CREATE TABLE `tb_alokasi` (
  `id` int(11) NOT NULL,
  `alokasi` varchar(100) NOT NULL,
  `kota` varchar(100) NOT NULL,
  `tahun` int(100) NOT NULL,
  `jumlah` bigint(100) NOT NULL,
  `deskripsi` varchar(255) NOT NULL,
  `status` varchar(255) NOT NULL COMMENT 'revisi,setuju,tidak setuju',
  `catatan` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tb_alokasi`
--

INSERT INTO `tb_alokasi` (`id`, `alokasi`, `kota`, `tahun`, `jumlah`, `deskripsi`, `status`, `catatan`) VALUES
(1, 'pendidikan', 'Kab. Berau', 2024, 250000000000, 'Dana BOS', 'setuju', ''),
(2, 'kesehatan', 'Kab. Berau', 2024, 250000000000, 'Puskesmas', 'setuju', ''),
(3, 'infrastruktur', 'Kab. Berau', 2024, 250000000000, 'Pengembangan Infrastruktur Beraw', 'setuju', '');

-- --------------------------------------------------------

--
-- Table structure for table `tb_anggaran`
--

CREATE TABLE `tb_anggaran` (
  `id` int(11) NOT NULL,
  `kota` varchar(100) NOT NULL,
  `tahun` int(100) NOT NULL,
  `total` bigint(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tb_anggaran`
--

INSERT INTO `tb_anggaran` (`id`, `kota`, `tahun`, `total`) VALUES
(1, 'Kab. Berau', 2024, 1000000000000);

-- --------------------------------------------------------

--
-- Table structure for table `tb_pendapatan`
--

CREATE TABLE `tb_pendapatan` (
  `id` int(11) NOT NULL,
  `nama_pendapatan` varchar(100) NOT NULL,
  `kota` varchar(100) NOT NULL,
  `total` bigint(100) NOT NULL,
  `tahun` int(100) NOT NULL,
  `deskripsi` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tb_user`
--

CREATE TABLE `tb_user` (
  `id_user` int(11) NOT NULL,
  `nama` varchar(255) NOT NULL,
  `username` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL,
  `role` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tb_user`
--

INSERT INTO `tb_user` (`id_user`, `nama`, `username`, `password`, `role`) VALUES
(1, 'admin', 'kepala', '123', 'admin'),
(2, 'zaid', 'pegawai', '123', 'user'),
(3, 'admin', 'admin', '123', 'super'),
(4, 'Ujang Mahendra', 'umahendra', 'ujang', 'admin'),
(5, 'Udin Mahendra', 'udinmah', '5510007174', 'user');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `tb_alokasi`
--
ALTER TABLE `tb_alokasi`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `tb_anggaran`
--
ALTER TABLE `tb_anggaran`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `tb_pendapatan`
--
ALTER TABLE `tb_pendapatan`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `tb_user`
--
ALTER TABLE `tb_user`
  ADD PRIMARY KEY (`id_user`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `tb_alokasi`
--
ALTER TABLE `tb_alokasi`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `tb_anggaran`
--
ALTER TABLE `tb_anggaran`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `tb_pendapatan`
--
ALTER TABLE `tb_pendapatan`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `tb_user`
--
ALTER TABLE `tb_user`
  MODIFY `id_user` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
