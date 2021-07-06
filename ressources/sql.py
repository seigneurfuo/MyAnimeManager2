"""Fichier qui contiends la stucture des tables"""

# ----- Série -----
serieCreateTableQuery = """
CREATE TABLE Serie (
    serie_id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    serie_sort_id INTEGER,
    serie_title  TEXT,
    serie_liked  INTEGER NOT NULL,
    serie_path   TEXT
);"""

serieDeleteFromSeriesQuery = """
DELETE FROM serie 
WHERE serie_id = :serie_id
"""

serieDeleteFromPlanningQuery = """
DELETE FROM planning 
WHERE planning_fk_serie_id = :serie_id
"""

seriesGetListQuery = """
SELECT * 
FROM serie 
ORDER BY serie_sort_id, serie_title
"""

seriesGetListWhereQuery = """
SELECT * 
FROM serie 
WHERE serie_title LIKE(:searchPatern) 
ORDER BY serie_sort_id, serie_title
"""

seasonCreateTableQuery = """
CREATE TABLE Season (
    season_id              INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    season_sort_id          INTEGER,
    season_title           TEXT,
    season_description     TEXT,
    season_release_year     INTEGER,
    season_studio          TEXT,
    season_episodes        INTEGER NOT NULL,
    season_watched_episodes INTEGER NOT NULL,
    season_fk_serie_id       INTEGER NOT NULL,
    season_fansub_team      TEXT,
    season_language        INTEGER NOT NULL,
    season_state           INTEGER NOT NULL,
    season_view_count       INTEGER NOT NULL,
    season_notes           TEXT,
    anidb TEXT,
    animeka TEXT,
    animekun TEXT,
    animenewsnetwork TEXT,
    myanimelist TEXT,
    planetejeunesse TEXT,
    FOREIGN KEY (season_fk_serie_id) REFERENCES Serie (serie_id) 
);"""

seasonDeleteFromSeasonsWhereSerie_idQuery = """
DELETE FROM season 
WHERE season_fk_serie_id = :serie_id
"""

seasonDeleteFromSeasonsQuery = """
DELETE FROM season WHERE season_id = :season_id
"""

seasonsGetListQuery = """
SELECT * 
FROM season, serie 
WHERE season_fk_serie_id == serie_id 
AND serie_id = :serie_id ORDER BY season_sort_id
"""

seasonDeleteFromPlanningQuery = """
DELETE FROM planning
WHERE planning_fk_season_id = :season_id"""

planningCreateTableQuery = """    
CREATE TABLE Planning (
    planning_id         INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    planning_date       DATE    NOT NULL,
    planning_fk_serie_id  INTEGER NOT NULL,
    planning_fk_season_id INTEGER NOT NULL,
    planning_episode_id  INTEGER NOT NULL,
    FOREIGN KEY (planning_fk_season_id) REFERENCES Season (season_id),
    FOREIGN KEY (planning_fk_serie_id) REFERENCES Serie (serie_id) 
);"""

notesCreateTableQuery = """
CREATE TABLE Notes (
    notes_page_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    notes_data   TEXT
);"""

# ----- Dernier animé vu -----
lastEpisodeWatchedDate = """
select planning.planning_date from planning
order by planning.planning_date desc"""

planningDateFromPlanningQuery = """
SELECT distinct planning_date from Planning
"""

getDataForTheChoosenDay = """
SELECT * FROM Planning, Serie, Season
WHERE planning_fk_serie_id = serie_id
AND planning_fk_season_id = season_id
AND planning_date = :planning_date
"""

planningAddEpisodeToWatchedList = """
INSERT INTO Planning (
    planning_id, planning_date, planning_fk_serie_id, planning_fk_season_id, planning_episode_id) 
    VALUES (NULL, :selected_date, :serie_id, :season_id, :season_current_episode_id)
"""

planningRemoveEpisodeFromWatchedList = """
DELETE FROM Planning 
WHERE planning_id = :planning_id
"""

planningSetCurrentEpisodeTo0 = """
UPDATE season 
SET season_watched_episodes = 0 
WHERE season_id = :season_id
"""

planningIncrementEpisode = """
UPDATE season 
SET season_watched_episodes = :season_watched_episodes 
WHERE season_id = :season_id
"""

planningSetSeasonToFinished = """
UPDATE season 
SET season_state = 3 
WHERE season_id = :season_id
"""

planningIncrementSeasonViewCount = """
UPDATE season 
SET season_view_count = season_view_count + 1 WHERE season_id = :season_id
"""

planningFillWithWatchingSeries = """
SELECT * 
FROM Serie, Season
WHERE season_fk_serie_id = serie_id
AND season_state == 2
AND season_watched_episodes < season_episodes
"""

planningEpisodesFillWithAll = """
SELECT * 
FROM Serie, Season
WHERE season_fk_serie_id = serie_id
AND season_state IN (1, 2)
AND season_watched_episodes < season_episodes
ORDER BY season_watched_episodes
"""

notesGet = """
SELECT * FROM Notes
"""

notesSave = """
UPDATE notes 
SET notes_data = :notes_data 
WHERE notes_page_id = 1
"""

getDatesListForSeasonId = """
SELECT planning_date, GROUP_CONCAT(planning_episode_id, ', ') AS episodes
FROM Planning
WHERE planning_fk_season_id = :season_id
GROUP BY planning_date
ORDER BY planning_date ASC
"""

getFullSeriesList = """
SELECT Serie.serie_sort_id, Serie.serie_title, Season.season_sort_id, Season.season_title, Season.season_episodes, Season.season_release_year
FROM Season
LEFT JOIN Serie ON Serie.serie_id = Season.season_fk_serie_id
WHERE Serie.serie_sort_id > 0
ORDER BY Serie.serie_sort_id, Season.serie_sort_id
"""