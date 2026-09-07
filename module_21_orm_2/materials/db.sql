-- таблица книг в библиотеке books
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    count INTEGER DEFAULT 1,
    release_date DATE NOT NULL,
    author_id INTEGER NOT NULL
);

-- таблица авторов authors
CREATE TABLE IF NOT EXISTS authors (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    surname TEXT NOT NULL
);

-- таблица читателей students
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    average_score FLOAT NOT NULL,
    scholarship BOOLEAN NOT NULL
);

-- Проверка формата телефона перед добавлением студента
CREATE TRIGGER IF NOT EXISTS validate_student_phone_before_insert
BEFORE INSERT ON students
FOR EACH ROW
WHEN NEW.phone NOT GLOB '+7(9[0-9][0-9])-[0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
BEGIN
    SELECT RAISE(
        ABORT,
        'Неверный формат телефона. Используйте: +7(9XX)-XXX-XX-XX'
    );
END;

-- таблица выдачи книг студентам receiving_books
CREATE TABLE IF NOT EXISTS receiving_books (
    id INTEGER PRIMARY KEY,
    book_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    date_of_issue DATETIME NOT NULL,
    date_of_return DATETIME
);