-- ====================================================
-- Database: ds_lab
-- Data Science Laboratory Portal
-- Mohan Babu University (MBU)
-- ====================================================

CREATE DATABASE IF NOT EXISTS ds_lab CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ds_lab;

-- Table: student
CREATE TABLE IF NOT EXISTS student (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL DEFAULT 'Shanmukhi',
    roll_no VARCHAR(50) NOT NULL DEFAULT '24102A030132',
    section VARCHAR(20) NOT NULL DEFAULT 'DS-3',
    branch VARCHAR(100) NOT NULL DEFAULT 'Data Science',
    subject VARCHAR(100) NOT NULL DEFAULT 'Data Science',
    faculty VARCHAR(100) NOT NULL DEFAULT 'Faculty In-Charge',
    photo_url VARCHAR(255) DEFAULT '/static/images/shanmukhi-profile.png',
    github_url VARCHAR(255) DEFAULT 'https://github.com/shanmukhi-06',
    linkedin_url VARCHAR(255) DEFAULT '',
    website_url VARCHAR(255) DEFAULT 'https://github.com/shanmukhi-06'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: experiments
CREATE TABLE IF NOT EXISTS experiments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    experiment_no VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL,
    short_description TEXT NOT NULL,
    d2_heading VARCHAR(255) DEFAULT 'Long Description',
    long_content LONGTEXT NOT NULL,
    github_url VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: experiment_media
CREATE TABLE IF NOT EXISTS experiment_media (
    id INT AUTO_INCREMENT PRIMARY KEY,
    experiment_id INT NOT NULL,
    media_type VARCHAR(50) NOT NULL, -- 'cover_image' or 'video'
    media_url VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_exp_media_experiment
        FOREIGN KEY (experiment_id) REFERENCES experiments(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: modules
CREATE TABLE IF NOT EXISTS modules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    module_no VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    topics TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: tools
CREATE TABLE IF NOT EXISTS tools (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    tool_url VARCHAR(255) DEFAULT '',
    icon_url VARCHAR(255) DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: resources
CREATE TABLE IF NOT EXISTS resources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    link_url VARCHAR(255) DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Seed default student record if empty
INSERT INTO student (id, name, roll_no, section, branch, subject, faculty, photo_url, github_url, linkedin_url, website_url)
SELECT 1, 'Shanmukhi', '24102A030132', 'DS-3', 'Data Science', 'Data Science', 'Faculty In-Charge', '/static/images/shanmukhi-profile.png', 'https://github.com/shanmukhi-06', '', 'https://github.com/shanmukhi-06'
WHERE NOT EXISTS (SELECT 1 FROM student WHERE id = 1);
