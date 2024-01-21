DROP DATABASE poc_db;
CREATE DATABASE poc_db;

USE poc_db;
create table memo (
    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    msg VARCHAR(255) NOT NULL,
    unique(title)
)