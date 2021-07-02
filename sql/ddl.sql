CREATE TABLE duo_langs (
    id   VARCHAR (3)  PRIMARY KEY
                      NOT NULL,
    lang VARCHAR (50) UNIQUE
                      NOT NULL,
    taal VARCHAR (50) UNIQUE
                      NOT NULL
);

CREATE TABLE duo_data (
    id                   VARCHAR (3) NOT NULL,
    date                 DATE        NOT NULL,
    points               INTEGER,
    level                INTEGER,
    level_progress       INTEGER,
    level_percent        INTEGER,
    level_points         INTEGER,
    level_left           INTEGER,
    next_level           INTEGER,
    num_skills_learned   INTEGER,
    points_rank          INTEGER,
    PRIMARY KEY (
        id ASC,
        date ASC
    ),
    FOREIGN KEY (
        id
    )
    REFERENCES duo_langs (id)
);

CREATE TABLE duo_status (
    id                   VARCHAR (3) NOT NULL,
    points               INTEGER,
    level                INTEGER,
    level_progress       INTEGER,
    level_percent        INTEGER,
    level_points         INTEGER,
    level_left           INTEGER,
    next_level           INTEGER,
    num_skills_learned   INTEGER,
    points_rank          INTEGER,
    streak_start         DATE,
    streak_end           DATE,
    PRIMARY KEY (
        id ASC
    ),
    FOREIGN KEY (
        id
    )
    REFERENCES duo_langs (id)
);
