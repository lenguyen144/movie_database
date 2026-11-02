CREATE DATABASE MOVIE_DATABASE;

USE MOVIE_DATABASE;


CREATE TABLE PRODUCER (
    ProducerID INT AUTO_INCREMENT,
    CompanyName VARCHAR(150) NOT NULL UNIQUE,
    Country VARCHAR(50),

    PRIMARY KEY (ProducerID)
);


CREATE TABLE MOVIE (
    MovieID INT AUTO_INCREMENT,
    Title VARCHAR(150) NOT NULL,
    Duration INT NOT NULL,
    Genre VARCHAR(50) NOT NULL,
    Plot TEXT,
    ReleaseYear INT,
    ProducerID INT NOT NULL,

    PRIMARY KEY (MovieID),

    FOREIGN KEY (ProducerID)
        REFERENCES PRODUCER(ProducerID),

    CHECK (Duration > 0),
    CHECK (ReleaseYear IS NULL OR ReleaseYear > 0)
);

