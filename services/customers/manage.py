# services/customers/manage.py

from flask.cli import FlaskGroup

from project import app, db, User  # nuevo

cli = FlaskGroup(app)

# nuevo
@cli.command()
def recreate_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


if __name__ == '__main__':
    cli()
