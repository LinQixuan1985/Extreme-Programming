-- 创建数据库（如尚未存在）
CREATE DATABASE IF NOT EXISTS contacts_db 
  CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;

USE contacts_db;

-- 创建表（支持 JSON 和布尔类型）
CREATE TABLE IF NOT EXISTS t_contact (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    phone_numbers JSON NOT NULL,
    emails JSON NOT NULL,
    addresses JSON NOT NULL,
    socials JSON NOT NULL,
    is_bookmarked BOOLEAN NOT NULL DEFAULT FALSE,
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SELECT DATABASE();

SHOW TABLES;

-- 删除旧表（谨慎！）
-- DROP TABLE IF EXISTS t_contact_detail;
-- DROP TABLE IF EXISTS t_contact;
