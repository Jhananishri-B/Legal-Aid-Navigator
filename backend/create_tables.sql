-- Legal Aid Navigator – MySQL / TiDB DDL
-- Run this in the TiDB SQL console (or any MySQL client with admin rights)
-- Replace `sys` with your actual database name if different.

CREATE DATABASE IF NOT EXISTS `legal_aid`;
USE `legal_aid`;

-- ── Users ──────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `users` (
    `id`         VARCHAR(36)  NOT NULL PRIMARY KEY,
    `username`   VARCHAR(100) NOT NULL UNIQUE,
    `email`      VARCHAR(255) NOT NULL UNIQUE,
    `full_name`  VARCHAR(200),
    `hashed_pw`  VARCHAR(255) NOT NULL,
    `created_at` DATETIME     DEFAULT NOW()
);

-- ── Legal Aid Requests ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `legal_aid_requests` (
    `id`                    VARCHAR(36)  NOT NULL PRIMARY KEY,
    `request_id`            VARCHAR(20)  NOT NULL UNIQUE,
    `user_id`               VARCHAR(36)  NOT NULL,
    `status`                VARCHAR(30)  DEFAULT 'in_progress',
    `current_stage`         INT          DEFAULT 1,
    -- Location
    `country`               VARCHAR(100),
    `state`                 VARCHAR(100),
    `district`              VARCHAR(100),
    `city`                  VARCHAR(150),
    `pin_code`              VARCHAR(20),
    -- Legal Issue
    `issue_type`            VARCHAR(150),
    `issue_description`     TEXT,
    `court_case_in_progress` VARCHAR(20),
    `court_deadline`        VARCHAR(50),
    `urgency`               VARCHAR(20),
    -- Eligibility
    `eligibility_category`  VARCHAR(150),
    `eligibility_details`   TEXT,
    `supporting_document`   VARCHAR(20),
    -- Contact
    `full_name`             VARCHAR(200),
    `mobile_number`         VARCHAR(20),
    `email`                 VARCHAR(255),
    `preferred_contact`     VARCHAR(20),
    `consultation_mode`     VARCHAR(20),
    -- Appointment
    `preferred_date`        VARCHAR(30),
    `preferred_time_slot`   VARCHAR(50),
    `appt_mode`             VARCHAR(20),
    `alt_date`              VARCHAR(30),
    `alt_time_slot`         VARCHAR(50),
    `additional_notes`      TEXT,
    `created_at`            DATETIME DEFAULT NOW(),
    `updated_at`            DATETIME DEFAULT NOW() ON UPDATE NOW(),
    CONSTRAINT `fk_req_user` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`)
);

-- ── Workflow Stages ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `workflow_stages` (
    `id`           VARCHAR(36)  NOT NULL PRIMARY KEY,
    `request_id`   VARCHAR(36)  NOT NULL,
    `stage_number` INT          NOT NULL,
    `name`         VARCHAR(100) NOT NULL,
    `status`       VARCHAR(30)  DEFAULT 'pending',
    `started_at`   DATETIME,
    `completed_at` DATETIME,
    `error`        TEXT,
    `result_json`  TEXT,
    CONSTRAINT `fk_stage_req` FOREIGN KEY (`request_id`) REFERENCES `legal_aid_requests`(`id`) ON DELETE CASCADE
);

-- ── Workflow Subtasks ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `workflow_subtasks` (
    `id`           VARCHAR(36)  NOT NULL PRIMARY KEY,
    `stage_id`     VARCHAR(36)  NOT NULL,
    `order`        INT          DEFAULT 0,
    `label`        VARCHAR(255) NOT NULL,
    `description`  VARCHAR(500),
    `status`       VARCHAR(30)  DEFAULT 'pending',
    `completed_at` DATETIME,
    `error`        TEXT,
    CONSTRAINT `fk_subtask_stage` FOREIGN KEY (`stage_id`) REFERENCES `workflow_stages`(`id`) ON DELETE CASCADE
);
