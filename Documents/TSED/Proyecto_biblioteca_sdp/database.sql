-- Ejecuta este script en MySQL Workbench o tu consola MySQL
-- antes de correr la aplicación

CREATE DATABASE IF NOT EXISTS biblioteca_db;
USE biblioteca_db;

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS libros (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    autor VARCHAR(100) NOT NULL,
    cantidad INT NOT NULL DEFAULT 0
);
