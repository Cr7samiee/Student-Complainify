-- Complainify Database Setup
-- Run this in phpMyAdmin or via: mysql -u root -p < complainify.sql

CREATE DATABASE IF NOT EXISTS complainify CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE complainify;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fullname VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(15),
    plain_password VARCHAR(100),
    password VARCHAR(255) NOT NULL,
    role ENUM('student','admin') NOT NULL DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Complaints table
CREATE TABLE IF NOT EXISTS complaints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id VARCHAR(20) NOT NULL UNIQUE,
    user_id INT,
    fullname VARCHAR(100),
    email VARCHAR(100),
    category VARCHAR(50) NOT NULL,
    priority ENUM('Low','Medium','High') NOT NULL DEFAULT 'Medium',
    subject VARCHAR(200) NOT NULL,
    description TEXT,
    status ENUM('Pending','In Progress','Resolved') NOT NULL DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Sample data
INSERT INTO users (fullname, email, phone, plain_password, password, role) VALUES
('Ram Sharma', 'ram@gmail.com', '9812345678', 'pass123', SHA2('pass123', 256), 'student'),
('Admin User', 'admin@complainify.edu', '9800000000', 'admin123', SHA2('admin123', 256), 'admin');

INSERT INTO complaints (ticket_id, user_id, fullname, email, category, priority, subject, description, status) VALUES
('CMP-1024', 1, 'Ram Sharma', 'ram@gmail.com', 'Academics', 'High', 'Missing Semester Credits', 'I am missing 2 credits from last semester transcript.', 'Pending'),
('CMP-1023', 1, 'Ram Sharma', 'ram@gmail.com', 'Hostels', 'Medium', 'Hostel Water Issue', 'No hot water in Block C since 2 days.', 'In Progress'),
('CMP-1022', 1, 'Ram Sharma', 'ram@gmail.com', 'IT Support', 'Low', 'WiFi Connectivity', 'Library WiFi is very slow.', 'Resolved');
