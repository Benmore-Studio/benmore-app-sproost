# Define your Django management command
MANAGE=python manage.py

# .PHONY ensures these commands are treated as targets without dependencies
.PHONY: run migrate migrations shell superuser \
        sqlflush dbshell collectstatic test sqlmigrate postgres_migrate \
        sqlite_migrate postgres_flush sqlite_flush postgres_dbshell sqlite_dbshell

# Run the development server
run:
	$(MANAGE) runserver

# Create database migrations
migrations:
	$(MANAGE) makemigrations

# Apply migrations
migrate:
	$(MANAGE) migrate

# Open the Django shell
shell:
	$(MANAGE) shell

# Create a superuser
superuser:
	$(MANAGE) createsuperuser

# Flush the database (remove all data but keep the schema)
sqlflush:
	$(MANAGE) flush --no-input

# Run tests
test:
	$(MANAGE) test

# Run a specific SQL migration
sqlmigrate:
	$(MANAGE) sqlmigrate $(app) $(migration)

# Collect static files
collectstatic:
	$(MANAGE) collectstatic --no-input

# Open the database shell for PostgreSQL
postgres_dbshell:
	DATABASE_URL=$(DATABASE_URL) $(MANAGE) dbshell

# Open the database shell for SQLite
sqlite_dbshell:
	sqlite3 $(SQLITE_PATH)

# Apply migrations for PostgreSQL
postgres_migrate:
	DATABASE_URL=$(DATABASE_URL) $(MANAGE) migrate

# Apply migrations for SQLite
sqlite_migrate:
	$(MANAGE) migrate --database=sqlite

# Flush PostgreSQL database
postgres_flush:
	DATABASE_URL=$(DATABASE_URL) $(MANAGE) flush --no-input

# Flush SQLite database
sqlite_flush:
	$(MANAGE) flush --no-input --database=sqlite
