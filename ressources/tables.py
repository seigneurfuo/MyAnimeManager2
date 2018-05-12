"""Fichier qui contiends la stucture des tables """

serieTableQuery = """
CREATE TABLE Serie (
    serieId     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    serieSortId INTEGER,
    serieTitle  TEXT,
    serieLiked  INTEGER NOT NULL,
    seriePath   TEXT
);"""

seasonTableQuery = """
CREATE TABLE Season (
    seasonId              INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    seasonSortId          INTEGER,
    seasonTitle           TEXT,
    seasonDescription     TEXT,
    seasonReleaseYear     INTEGER,
    seasonStudio          TEXT,
    seasonEpisodes        INTEGER NOT NULL,
    seasonWatchedEpisodes INTEGER NOT NULL,
    seasonFKserieId       INTEGER NOT NULL,
    seasonFansubTeam      TEXT,
    seasonState           INTEGER NOT NULL,
    seasonViewCount       INTEGER NOT NULL,
    seasonNotes           TEXT,
    FOREIGN KEY (seasonFKserieId) REFERENCES Serie (serieId) 
);"""

planningTableQuery = """    
CREATE TABLE Planning (
    planningId         INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    planningDate       DATE    NOT NULL,
    planningFKserieId  INTEGER NOT NULL,
    planningFKseasonId INTEGER NOT NULL,
    planningEpisodeId  INTEGER NOT NULL,
    FOREIGN KEY (planningFKseasonId) REFERENCES Season (seasonId),
    FOREIGN KEY (planningFKserieId) REFERENCES Serie (serieId) 
);"""

notesTableQuery = """
CREATE TABLE Notes (
    notesPageId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    notesData   TEXT
);"""