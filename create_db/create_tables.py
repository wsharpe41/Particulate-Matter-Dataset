import sqlalchemy as db


# Create the database
engine = db.create_engine('sqlite:///pm_map.db')
connection = engine.connect()
metadata = db.MetaData()


measurements = db.Table('measurements', metadata,
                        db.Column('measurement_id', db.Integer(), primary_key=True),
                        db.Column('timestamp', db.DateTime()),
                        db.Column('pm', db.Float()),
                        db.Column('temperature', db.Float()),
                        db.Column('relative_humidity', db.Float()),
                        db.Column('rain', db.Float()),
                        db.Column('wind_speed10', db.Float()),
                        db.Column('wind_speed100', db.Float()),
                        db.Column('wind_direction10', db.Float()),
                        db.Column('wind_direction100', db.Float()),
                        db.Column('wind_gusts10', db.Float()),
                        db.Column('site_id', db.Integer(), db.ForeignKey('sites.site_id'))  # Foreign key relationship
)


# Create a table for the sites
sites = db.Table('sites', metadata,
    db.Column('site_id', db.Integer(), primary_key=True),
    db.Column('latitude', db.Float()),
    db.Column('longitude', db.Float()),
    db.Column('elevation', db.Float()),
)

# Create all tables
metadata.create_all(engine)

    