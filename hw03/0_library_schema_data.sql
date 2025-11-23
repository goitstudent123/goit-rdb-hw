SET search_path TO LibraryManagement;

-- ============================
-- Authors (5)
-- ============================
INSERT INTO authors (author_name) VALUES
('George Orwell'),
('J. K. Rowling'),
('Stephen King'),
('Agatha Christie'),
('Ernest Hemingway');

-- ============================
-- Genres (3)
-- ============================
INSERT INTO genres (genre_name) VALUES
('Fiction'),
('Mystery'),
('Fantasy');

-- ============================
-- Users (5)
-- ============================
INSERT INTO users (username, email) VALUES
('alice',   'alice@example.com'),
('bob',     'bob@example.com'),
('charlie', 'charlie@example.com'),
('diana',   'diana@example.com'),
('edward',  'edward@example.com');

-- ============================
-- Books (20)
-- ============================
INSERT INTO books (title, publication_year, author_id, genre_id) VALUES
('1984',                 1949, 1, 1),
('Animal Farm',          1945, 1, 1),
('Harry Potter 1',       1997, 2, 3),
('Harry Potter 2',       1998, 2, 3),
('The Shining',          1977, 3, 1),
('It',                   1986, 3, 1),
('Murder on the Orient', 1934, 4, 2),
('And Then There Were',  1939, 4, 2),
('The Old Man and Sea',  1952, 5, 1),
('For Whom the Bell',    1940, 5, 1),
('Carrie',               1974, 3, 1),
('The Stand',            1978, 3, 1),
('Misery',               1987, 3, 1),
('The Casual Vacancy',   2012, 2, 1),
('Lethal White',         2018, 2, 2),
('Death on the Nile',    1937, 4, 2),
('The Sun Also Rises',   1926, 5, 1),
('Green Hills of Africa',1935, 5, 1),
('Night Shift',          1978, 3, 1),
('The Long Walk',        1979, 3, 1);

-- ============================
-- Borrowed books (3 records)
-- ============================
INSERT INTO borrowed_books (book_id, user_id, borrow_date, return_date) VALUES
(1,  2, '2025-01-10', NULL),   -- Bob має "1984"
(7,  1, '2025-02-02', NULL),   -- Alice має "Murder on the Orient"
(11, 4, '2025-02-15', NULL);   -- Diana має "Carrie"
