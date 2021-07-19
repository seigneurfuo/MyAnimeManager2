from peewee import *

database = SqliteDatabase("/home/seigneurfuo/.myanimemanager2/database.sqlite3")


class UnknownField(object):
    def __init__(self, *_, **__): pass


class BaseModel(Model):
    class Meta:
        database = database


class Notes(BaseModel):
    notes_page_id = AutoField()
    notes_data = TextField(null=True)

    class Meta:
        table_name = 'Notes'


class Serie(BaseModel):
    serie_id = AutoField()
    serie_sort_id = IntegerField(null=True)
    serie_title = TextField(null=True)
    serie_liked = IntegerField()
    serie_path = TextField(null=True)

    class Meta:
        table_name = 'Serie'


class Season(BaseModel):
    season_id = AutoField()
    season_sort_id = IntegerField(null=True)
    season_title = TextField(null=True)
    season_description = TextField(null=True)
    season_release_year = IntegerField(null=True)
    season_studio = TextField(null=True)
    season_episodes = IntegerField()
    season_watched_episodes = IntegerField()
    season_fk_serie = ForeignKeyField(column_name='season_fk_serie_id', model=Serie)
    season_fansub_team = TextField(null=True)
    season_language = IntegerField(null=True)
    season_state = IntegerField()
    season_view_count = IntegerField()
    season_notes = TextField(null=True)
    anidb = TextField(null=True)
    animeka = TextField(null=True)
    animekun = TextField(null=True)
    animenewsnetwork = TextField(null=True)
    myanimelist = TextField(null=True)
    planetejeunesse = TextField(null=True)

    class Meta:
        table_name = 'Season'


class Planning(BaseModel):
    planning_id = AutoField()
    planning_date = DateField()
    planning_fk_serie = ForeignKeyField(column_name='planning_fk_serie_id', model=Serie)
    planning_fk_season = ForeignKeyField(column_name='planning_fk_season_id', model=Season)
    planning_episode_id = IntegerField()

    class Meta:
        table_name = 'Planning'


class SqliteSequence(BaseModel):
    name = BareField(null=True)
    seq = BareField(null=True)

    class Meta:
        table_name = 'sqlite_sequence'
        primary_key = False
