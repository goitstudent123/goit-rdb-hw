-- Create schema
CREATE SCHEMA IF NOT EXISTS LibraryManagement;
SET search_path TO LibraryManagement;

-- ============================
-- Table: authors
-- ============================
CREATE TABLE authors (
    author_id   SERIAL PRIMARY KEY,
    author_name VARCHAR NOT NULL
);

-- ============================
-- Table: genres
-- ============================
CREATE TABLE genres (
    genre_id   SERIAL PRIMARY KEY,
    genre_name VARCHAR NOT NULL
);

-- ============================
-- Table: books
-- ============================
CREATE TABLE books (
    book_id          SERIAL PRIMARY KEY,
    title            VARCHAR NOT NULL,
    publication_year INT,
    author_id        INT NOT NULL,
    genre_id         INT NOT NULL,

    CONSTRAINT fk_books_author
        FOREIGN KEY (author_id)
        REFERENCES authors (author_id),

    CONSTRAINT fk_books_genre
        FOREIGN KEY (genre_id)
        REFERENCES genres (genre_id)
);

-- ============================
-- Table: users
-- ============================
CREATE TABLE users (
    user_id  SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL,
    email    VARCHAR NOT NULL
);

-- ============================
-- Table: borrowed_books
-- ============================
CREATE TABLE borrowed_books (
    borrow_id   SERIAL PRIMARY KEY,
    book_id     INT NOT NULL,
    user_id     INT NOT NULL,
    borrow_date DATE NOT NULL,
    return_date DATE,

    CONSTRAINT fk_borrow_book
        FOREIGN KEY (book_id)
        REFERENCES books (book_id),

    CONSTRAINT fk_borrow_user
        FOREIGN KEY (user_id)
        REFERENCES users (user_id)
);