CREATE DATABASE IF NOT EXISTS cute_photobooth
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE cute_photobooth;

CREATE TABLE IF NOT EXISTS sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    guest_name VARCHAR(60) NOT NULL DEFAULT 'Guest',
    caption VARCHAR(45) NOT NULL DEFAULT 'my cute day',
    frame_style VARCHAR(20) NOT NULL DEFAULT 'pink',
    upload_file VARCHAR(255) NOT NULL,
    result_file VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- Tabel akun untuk fitur register dan login.
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    username VARCHAR(30) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
