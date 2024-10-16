DROP USER IF EXISTS 'admin'@'%';
CREATE USER IF NOT EXISTS 'admin'@'%' IDENTIFIED BY 'root';
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%';
FLUSH PRIVILEGES;

CREATE DATABASE IF NOT EXISTS `audio_chat` DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

USE `audio_chat`;

CREATE TABLE IF NOT EXISTS `characters` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `avatar_uri` VARCHAR(255) NOT NULL,
    `gpt_model_path` VARCHAR(255) NOT NULL,
    `sovits_model_path` VARCHAR(255) NOT NULL,
    `refer_path` VARCHAR(255) NOT NULL,
    `refer_text` VARCHAR(255) NOT NULL
);