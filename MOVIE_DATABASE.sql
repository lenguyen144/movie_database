
-- ==========================================
-- DATABASE: MOVIE_DATABASE
-- LAB 1 - DATABASE DESIGN DOCUMENTATION
-- DBMS: MySQL
-- ==========================================

CREATE DATABASE MOVIE_DATABASE;

USE MOVIE_DATABASE;


-- ==========================================
-- 1. TABLE: PRODUCER
-- Store production company information
-- ==========================================

CREATE TABLE PRODUCER (
    ProducerID INT AUTO_INCREMENT,
    CompanyName VARCHAR(150) NOT NULL UNIQUE,
    Country VARCHAR(50),

    PRIMARY KEY (ProducerID)
) ENGINE=InnoDB;


-- ==========================================
-- 2. TABLE: GENRE
-- Store movie genre information
-- ==========================================

CREATE TABLE GENRE (
    GenreID INT AUTO_INCREMENT,
    GenreName VARCHAR(50) NOT NULL UNIQUE,

    PRIMARY KEY (GenreID)
) ENGINE=InnoDB;


-- ==========================================
-- 3. TABLE: MOVIE
-- Store movie information
-- ==========================================

CREATE TABLE MOVIE (
    MovieID INT AUTO_INCREMENT,
    Title VARCHAR(150) NOT NULL,
    Duration INT NOT NULL,
    Plot TEXT,
    ReleaseYear INT,
    ProducerID INT NOT NULL,

    PRIMARY KEY (MovieID),

    CONSTRAINT fk_movie_producer
        FOREIGN KEY (ProducerID)
        REFERENCES PRODUCER(ProducerID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CHECK (Duration > 0),
    CHECK (ReleaseYear IS NULL OR ReleaseYear > 0)
) ENGINE=InnoDB;


-- ==========================================
-- 4. TABLE: ACTOR
-- Store actor information
-- ==========================================

CREATE TABLE ACTOR (
    ActorID INT AUTO_INCREMENT,
    FullName VARCHAR(100) NOT NULL,
    DateOfBirth DATE,
    Nationality VARCHAR(50),

    PRIMARY KEY (ActorID)
) ENGINE=InnoDB;


-- ==========================================
-- 5. TABLE: DIRECTOR
-- Store director information
-- ==========================================

CREATE TABLE DIRECTOR (
    DirectorID INT AUTO_INCREMENT,
    FullName VARCHAR(100) NOT NULL,
    DateOfBirth DATE,
    Nationality VARCHAR(50),

    PRIMARY KEY (DirectorID)
) ENGINE=InnoDB;


-- ==========================================
-- 6. TABLE: MOVIE_ACTOR
-- Connect movies and actors
-- Store character names
-- ==========================================

CREATE TABLE MOVIE_ACTOR (
    MovieID INT NOT NULL,
    ActorID INT NOT NULL,
    CharacterName VARCHAR(100) NOT NULL,

    PRIMARY KEY (MovieID, ActorID),

    CONSTRAINT fk_movie_actor_movie
        FOREIGN KEY (MovieID)
        REFERENCES MOVIE(MovieID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_movie_actor_actor
        FOREIGN KEY (ActorID)
        REFERENCES ACTOR(ActorID)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB;


-- ==========================================
-- 7. TABLE: MOVIE_DIRECTOR
-- Connect movies and directors
-- ==========================================

CREATE TABLE MOVIE_DIRECTOR (
    MovieID INT NOT NULL,
    DirectorID INT NOT NULL,

    PRIMARY KEY (MovieID, DirectorID),

    CONSTRAINT fk_movie_director_movie
        FOREIGN KEY (MovieID)
        REFERENCES MOVIE(MovieID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_movie_director_director
        FOREIGN KEY (DirectorID)
        REFERENCES DIRECTOR(DirectorID)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB;


-- ==========================================
-- 8. TABLE: MOVIE_GENRE
-- Connect movies and genres
-- ==========================================

CREATE TABLE MOVIE_GENRE (
    MovieID INT NOT NULL,
    GenreID INT NOT NULL,

    PRIMARY KEY (MovieID, GenreID),

    CONSTRAINT fk_movie_genre_movie
        FOREIGN KEY (MovieID)
        REFERENCES MOVIE(MovieID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_movie_genre_genre
        FOREIGN KEY (GenreID)
        REFERENCES GENRE(GenreID)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB;


-- ==========================================
-- 9. TABLE: MOVIE_QUOTE
-- Store famous movie quotes
-- ==========================================

CREATE TABLE MOVIE_QUOTE (
    QuoteID INT AUTO_INCREMENT,
    MovieID INT NOT NULL,
    ActorID INT NOT NULL,
    QuoteText TEXT NOT NULL,

    PRIMARY KEY (QuoteID),

    CONSTRAINT fk_quote_movie_actor
        FOREIGN KEY (MovieID, ActorID)
        REFERENCES MOVIE_ACTOR(MovieID, ActorID)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- ==========================================
-- 10. INDEXES
-- Improve search performance
-- ==========================================

CREATE INDEX idx_movie_title
    ON MOVIE(Title);

CREATE INDEX idx_actor_fullname
    ON ACTOR(FullName);

