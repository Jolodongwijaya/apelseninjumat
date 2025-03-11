-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 20 Feb 2025 pada 05.23
-- Versi server: 10.4.28-MariaDB
-- Versi PHP: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `jadwal_apel`
--

-- --------------------------------------------------------

--
-- Struktur dari tabel `petugas`
--

CREATE TABLE `petugas` (
  `id` int(11) NOT NULL,
  `nama` varchar(255) NOT NULL,
  `peran` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `petugas`
--

INSERT INTO `petugas` (`id`, `nama`, `peran`) VALUES
(1, 'Muslich SAg MH', 'Ketua PA'),
(2, 'H Muhammad Nuruddin Lc MSI', 'Wakil PA'),
(3, 'Drs Muridi MH', 'Hakim'),
(4, 'Drs Agus Suntono MHI', 'Hakim'),
(5, 'Haitami SH MH', 'Hakim'),
(6, 'Kamali SAg', 'Hakim'),
(7, 'Agung Yusfantoro SH', 'Komandan'),
(8, 'Trie Endah Dahlia SH MH', 'MC'),
(9, 'Lailiya Rahmah SH', 'MC'),
(10, 'Driya Primasthi SE', 'MC'),
(11, 'Salma Venna Auliya SAP', 'MC'),
(12, 'Dadang Heri Purnomo AMd', '8 Nilai MA'),
(13, 'Ariyadi SH', '8 Nilai MA'),
(14, 'Haris Ali Murfi SH', '8 Nilai MA'),
(15, 'Aulia Rahman SH', '8 Nilai MA'),
(16, 'Dadang Heri Purnomo AMd', 'Ajudan'),
(17, 'Ariyadi SH', 'Ajudan'),
(18, 'Haris Ali Murfi SH', 'Ajudan');

-- --------------------------------------------------------

--
-- Struktur dari tabel `rotasi`
--

CREATE TABLE `rotasi` (
  `id` int(11) NOT NULL,
  `peran` varchar(50) NOT NULL,
  `posisi` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `rotasi`
--

INSERT INTO `rotasi` (`id`, `peran`, `posisi`) VALUES
(1, 'MC', 0),
(2, '8 Nilai MA', 0),
(3, 'Ajudan', 0),
(4, 'Ketua/Wakil', 0),
(5, 'Wakil', 0),
(6, 'Hakim', 0);

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `petugas`
--
ALTER TABLE `petugas`
  ADD PRIMARY KEY (`id`);

--
-- Indeks untuk tabel `rotasi`
--
ALTER TABLE `rotasi`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `peran` (`peran`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `petugas`
--
ALTER TABLE `petugas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT untuk tabel `rotasi`
--
ALTER TABLE `rotasi`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
