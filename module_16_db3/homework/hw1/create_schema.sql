PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS movie_cast;
DROP TABLE IF EXISTS movie_direction;
DROP TABLE IF EXISTS oscar_awarded;
DROP TABLE IF EXISTS actors;
DROP TABLE IF EXISTS director;
DROP TABLE IF EXISTS movie;


CREATE TABLE actors (
    act_id INTEGER PRIMARY KEY,
    act_first_name VARCHAR(50) NOT NULL,
    act_last_name VARCHAR(50) NOT NULL,
    act_gender VARCHAR(1)
);


CREATE TABLE movie (
    mov_id INTEGER PRIMARY KEY,
    mov_title VARCHAR(50) NOT NULL
);


CREATE TABLE director (
    dir_id INTEGER PRIMARY KEY,
    dir_first_name VARCHAR(50) NOT NULL,
    dir_last_name VARCHAR(50) NOT NULL
);


CREATE TABLE movie_cast (
    act_id INTEGER NOT NULL,
    mov_id INTEGER NOT NULL,
    role VARCHAR(50) NOT NULL,

    PRIMARY KEY (act_id, mov_id),

    CONSTRAINT fk_movie_cast_actor
        FOREIGN KEY (act_id)
        REFERENCES actors (act_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_movie_cast_movie
        FOREIGN KEY (mov_id)
        REFERENCES movie (mov_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);


CREATE TABLE oscar_awarded (
    award_id INTEGER PRIMARY KEY,
    mov_id INTEGER NOT NULL,

    CONSTRAINT fk_oscar_awarded_movie
        FOREIGN KEY (mov_id)
        REFERENCES movie (mov_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);


CREATE TABLE movie_direction (
    dir_id INTEGER NOT NULL,
    mov_id INTEGER NOT NULL,

    PRIMARY KEY (dir_id, mov_id),

    CONSTRAINT fk_movie_direction_director
        FOREIGN KEY (dir_id)
        REFERENCES director (dir_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_movie_direction_movie
        FOREIGN KEY (mov_id)
        REFERENCES movie (mov_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);