"""Fichier qui contiends la stucture des tables"""

# ----- Série -----
serieCreateTableQuery = """
CREATE TABLE Serie (
    serieId     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    serieSortId INTEGER,
    serieTitle  TEXT,
    serieLiked  INTEGER NOT NULL,
    seriePath   TEXT
);"""

serieDeleteFromSeriesQuery = """
DELETE FROM serie 
WHERE serieId = :serieId
"""

serieDeleteFromPlanningQuery = """
DELETE FROM planning 
WHERE planningFKserieId = :serieId
"""

seriesGetListQuery = """
SELECT * 
FROM serie 
ORDER BY serieSortId, serieTitle
"""

seriesGetListWhereQuery = """
SELECT * 
FROM serie 
WHERE serieTitle LIKE(:searchPatern) 
ORDER BY serieSortId, serieTitle
"""

seasonCreateTableQuery = """
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

seasonDeleteFromSeasonsWhereSerieIdQuery = """
DELETE FROM season 
WHERE seasonFKserieId = :serieId"
"""

seasonDeleteFromSeasonsQuery = """
DELETE FROM season WHERE seasonId = :seasonId
"""

seasonsGetListQuery = """
SELECT * 
FROM season, serie 
WHERE seasonFKserieId == serieId 
AND serieId = :serieId ORDER BY seasonSortId
"""

seasonDeleteFromPlanningQuery = """
DELETE FROM planning
WHERE planningFKseasonId = :seasonId"""

planningCreateTableQuery = """    
CREATE TABLE Planning (
    planningId         INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    planningDate       DATE    NOT NULL,
    planningFKserieId  INTEGER NOT NULL,
    planningFKseasonId INTEGER NOT NULL,
    planningEpisodeId  INTEGER NOT NULL,
    FOREIGN KEY (planningFKseasonId) REFERENCES Season (seasonId),
    FOREIGN KEY (planningFKserieId) REFERENCES Serie (serieId) 
);"""

notesCreateTableQuery = """
CREATE TABLE Notes (
    notesPageId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    notesData   TEXT
);"""

planningDateFromPlanningQuery = """
SELECT distinct planningDate from Planning
"""

getDataForTheChoosenDay = """
SELECT * FROM Planning, Serie, Season
WHERE planningFKserieId = serieId
AND planningFKseasonId = seasonId
AND planningDate = :planningDate
"""

planningAddEpisodeToWatchedList = """
INSERT INTO Planning (
    planningId, planningDate, planningFKserieId, planningFKseasonId, planningEpisodeId) 
    VALUES (NULL, :selectedDate, :serieId, :seasonId, :seasonCurrentEpisodeId)
"""

planningRemoveEpisodeFromWatchedList = """
DELETE FROM Planning 
WHERE planningId = :planningId
"""

planningSetCurrentEpisodeTo0 = """
UPDATE season 
SET seasonWatchedEpisodes = 0 
WHERE seasonId = :seasonId"
"""

planningIncrementEpisode = """
UPDATE season 
SET seasonWatchedEpisodes = :seasonWatchedEpisodes 
WHERE seasonId = :seasonId"
"""

planningSetSeasonToFinished = """
UPDATE season 
SET seasonState = 3 
WHERE seasonId = :seasonId"
"""

planningIncrementSeasonViewCount = """
UPDATE season 
SET seasonViewCount = seasonViewCount + 1 WHERE seasonId = :seasonId
"""

planningFillWithWatchingSeries = """
SELECT * 
FROM Serie, Season
WHERE seasonFKserieId = serieId
AND seasonState == 2
AND seasonWatchedEpisodes < seasonEpisodes
"""

planningEpisodesFillWithAll = """
SELECT * 
FROM Serie, Season
WHERE seasonFKserieId = serieId
AND seasonState IN (1, 2)
AND seasonWatchedEpisodes < seasonEpisodes
"""

notesGet = """
SELECT * FROM Notes
"""

notesSave = """
UPDATE notes 
SET notesData = :notesData 
WHERE notesPageId = 1
"""