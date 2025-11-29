-- Abilita il supporto per le chiavi esterne in SQLite
PRAGMA foreign_keys = ON;

-- Tabella AUTHOR (AUTORE)
-- PK: author_id
CREATE TABLE AUTHOR (
    author_id       INTEGER PRIMARY KEY,
    name            TEXT NOT NULL,
    surname         TEXT NOT NULL,
    nationality     TEXT,
    birth_date      TEXT,
    death_date      TEXT  -- data_morte è opzionale (*)
);

-- Tabella EMPLOYEE (DIPENDENTE)
-- PK: employee_id
CREATE TABLE EMPLOYEE (
    employee_id     INTEGER PRIMARY KEY,
    name            TEXT NOT NULL,
    surname         TEXT NOT NULL,
    role            TEXT,
    hire_date       TEXT NOT NULL,
    email           TEXT,
    phone           TEXT
);

-- Tabella ROOM (SALA)
-- PK: room_id
-- FK: responsible_employee_id (id_dipendente_responsabile)
CREATE TABLE ROOM (
    room_id                         INTEGER PRIMARY KEY,
    responsible_employee_id         INTEGER,
    name                            TEXT NOT NULL,
    capacity                        INTEGER,
    floor                           TEXT,
    type                            TEXT,
    FOREIGN KEY (responsible_employee_id) REFERENCES EMPLOYEE(employee_id)
);

-- Tabella READER (LETTORE)
-- PK: reader_id
CREATE TABLE READER (
    reader_id           INTEGER PRIMARY KEY,
    name                TEXT NOT NULL,
    surname             TEXT NOT NULL,
    email               TEXT,
    phone               TEXT,
    address             TEXT,
    subscription_date   TEXT NOT NULL
);

-- Tabella BOOK (LIBRO)
-- PK: book_id
-- FK: author_id
CREATE TABLE BOOK (
    book_id                 INTEGER PRIMARY KEY,
    author_id               INTEGER NOT NULL,
    title                   TEXT NOT NULL,
    publication_year        INTEGER,
    genre                   TEXT,
    num_copies              INTEGER,
    FOREIGN KEY (author_id) REFERENCES AUTHOR(author_id)
);

-- Tabella BOOK_LOAN (PRESTITO_LIBRO)
-- PK: (book_id, reader_id, loan_date)
-- FK: book_id, reader_id
-- return_date e notes sono opzionali (*)
CREATE TABLE BOOK_LOAN (
    book_id             INTEGER NOT NULL,
    reader_id           INTEGER NOT NULL,
    loan_date           TEXT NOT NULL,
    return_date         TEXT,  -- data_restituzione è opzionale (*)
    notes               TEXT,  -- note è opzionale (*)
    PRIMARY KEY (book_id, reader_id, loan_date),
    FOREIGN KEY (book_id) REFERENCES BOOK(book_id),
    FOREIGN KEY (reader_id) REFERENCES READER(reader_id)
);

-- Tabella ROOM_RESERVATION (PRENOTAZIONE_SALA)
-- PK: (reader_id, date, start_time)
-- FK: reader_id, room_id
-- notes è opzionale (*)
CREATE TABLE ROOM_RESERVATION (
    reader_id       INTEGER NOT NULL,
    date            TEXT NOT NULL,
    start_time      TEXT NOT NULL,
    end_time        TEXT NOT NULL,
    room_id         INTEGER NOT NULL,
    notes           TEXT,  -- note è opzionale (*)
    PRIMARY KEY (reader_id, date, start_time),
    FOREIGN KEY (reader_id) REFERENCES READER(reader_id),
    FOREIGN KEY (room_id) REFERENCES ROOM(room_id)
);