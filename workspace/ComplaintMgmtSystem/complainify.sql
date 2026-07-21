-- Complainify Database Setup
-- Run: mysql -u root < complainify.sql

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

-- Complaints table (full schema with all columns)
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
    sentiment VARCHAR(20) DEFAULT 'Neutral',
    sentiment_score FLOAT DEFAULT 0.0,
    assigned_to VARCHAR(100) DEFAULT NULL,
    assigned_at DATETIME DEFAULT NULL,
    resolved_at DATETIME DEFAULT NULL,
    admin_notes TEXT DEFAULT NULL,
    validated TINYINT(1) DEFAULT 0,
    email_sent TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- OTP table for forgot-password flow
CREATE TABLE IF NOT EXISTS otps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) NOT NULL,
    otp VARCHAR(6) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    used TINYINT(1) DEFAULT 0
);

-- Only add columns if they don't exist (safe for existing DBs)
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS assigned_to VARCHAR(100) DEFAULT NULL AFTER sentiment_score;
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS assigned_at DATETIME DEFAULT NULL AFTER assigned_to;
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS resolved_at DATETIME DEFAULT NULL AFTER assigned_at;
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS admin_notes TEXT DEFAULT NULL AFTER resolved_at;
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS validated TINYINT(1) DEFAULT 0 AFTER admin_notes;
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS email_sent TINYINT(1) DEFAULT 0 AFTER validated;

-- Sample users
INSERT IGNORE INTO users (id, fullname, email, phone, plain_password, password, role) VALUES
(1, 'Ram Sharma', 'ram@gmail.com', '9812345678', 'pass123', SHA2('pass123', 256), 'student'),
(2, 'Admin User', 'admin@complainify.edu', '9800000000', 'admin123', SHA2('admin123', 256), 'admin');

-- Sample complaints
INSERT IGNORE INTO complaints (ticket_id, user_id, fullname, email, category, priority, subject, description, status, sentiment, sentiment_score) VALUES
('CMP-1024', 1, 'Ram Sharma', 'ram@gmail.com', 'Academics', 'High', 'Missing Semester Credits', 'I am missing 2 credits from last semester transcript.', 'Pending', 'Negative', -1.5),
('CMP-1023', 1, 'Ram Sharma', 'ram@gmail.com', 'Hostels', 'Medium', 'Hostel Water Issue', 'No hot water in Block C since 2 days.', 'In Progress', 'Negative', -2.0),
('CMP-1022', 1, 'Ram Sharma', 'ram@gmail.com', 'IT Support', 'Low', 'WiFi Connectivity', 'Library WiFi is very slow.', 'Resolved', 'Neutral', 0.0);
