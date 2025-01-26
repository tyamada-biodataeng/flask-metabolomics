from datetime import datetime

import click
from flask import current_app, g
import psycopg
from psycopg.rows import dict_row


def get_db():
    if 'db' not in g:
        g.db = psycopg.connect(
            str(current_app.config['DATABASE_URL']),
            cursor_factory=dict_row
        )

    return g.db


def get_cursor():
    return get_db().cursor()


def commit():
    get_db().commit()


def rollback():
    get_db().rollback()


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        if e is None:
            db.commit()
        else:
            db.rollback()
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
