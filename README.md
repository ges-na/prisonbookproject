A workflow and data collection tool designed to track letters from incarcerated readers. Created for [Pittsburgh Prison Book Project](https://pghprisonbookproject.org/).

# Details

## What this tool does
- Track letters through different workflow stages.
- Create multiple users with different permissions (e.g. individual accounts, readonly account).
- Allow bulk changes to workflow stages (e.g. selecting multiple letters to move to the next stage).
- Provide a place to document per-letter issues.
- Create a record for each unique writer.
- Provide a place to record per-prison restrictions.
- Allow labeling of individuals as being in solitary or serving a life sentence.
- Create database backups.

## What this tool does not do*
\* But probably could, if you want to modify it for your local context.
- Track content of letters (e.g. books or genres requested).
- Track mailing info (e.g. unique package tracking info).
- Automatically provide statistics [planned functionality].

## Limitations
- This tool doesn't work out of the box. Anyone implementing it will need to have some understanding of Python, Django, Postgres, and web-hosting tools (the current main implementation of this project is hosted on fly.io).
- Context. This tool was written with a particular context in mind. What this means is that local requirements (workflow stage names, required/available fields, etc.) are at times particular to that context and may require adjustment if implemented elsewhere.
- Use of Django Admin. The interface is just the Django Admin. This works great for using it like a database with user-friendly forms. This does not work great if you want the look and feel to be different.

# Changelog
2025-11-21
* Added daily database backup to AWS (GitHub Action to pg_dump .sql format to S3 bucket)
* Tested restore from backup locally and on Fly
* Non-superusers can now edit prison address, notes, and restrictions

2025-08-19
* Add filters to People table
* Add custom Person queryset/manager
* Add No Longer In Custody labels / filter
* Remove Just PADA workflow status
* Bulk Letter discard action

2025-08-17
* Restructured project (added `src/` dir)
* Added fly.io dev server config
* Environment-based color scheme support
* Project Python3.10 -> 3.12

# Setup

## Create environment
1. Install [poetry](https://python-poetry.org/docs/#installation).
2. Create `.env` file (see `.env.example`). 
3. Activate virtual environment.
    - [optional] Install and use [direnv](https://direnv.net/) to make use of project `.envrc`.

## Set up database
1. Install `postgres` if needed.
2. Set up project database and postgres user.
```
CREATE DATABASE <database_name>;
CREATE ROLE <project_user> LOGIN PASSWORD '<project_user_pw>';
# GRANT ALL ON DATABASE <database_name> TO <project_user>;
\c <database_name>
GRANT USAGE, CREATE ON SCHEMA public to <project_user>;
```
Note: Values such as `database_name`, `project_user`, and `project_user_pw` must match the `DATABASE_URL` env var parameters.
3. From project root, run `./manage.py migrate`
4. From project root, run `./manage.py createsuperuser`

## Run server
Test connection and attempt to log in as the superuser created in the previous section: `./manage.py runserver`

## Set up fly.io connection
This section assumes you are connecting to an existing set of fly.io apps. If spinning up a new instance, you can use fly.io to take advantage of this project's existing `fly.toml` file or choose your own hosting platform.
1. Install [flyctl](https://fly.io/docs/flyctl/install/).
2. Run `fly apps list` and follow prompts to log in.

## Set up automatic backups
1. Requirements: GitHub repo, Amazon S3.
2. This functionality relies on [significa/fly-pg-dump-to-s3](https://github.com/significa/fly-pg-dump-to-s3), which has good setup instructions.
Notes:
- You should receive an email if your database backup fails.
- Make sure to test restoring from one of these db dumps on a non-production server, ideally on some regular schedule.

### Licensing / reuse
This project is licensed under [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html). If it is useful to your books to prisoners project, I'd be thrilled if you reuse/remix/implement it. If you have questions, [email me](mailto:gesinaface@gmail.com) or find me on [Bluesky](https://bsky.app/profile/gesina.bsky.social).
