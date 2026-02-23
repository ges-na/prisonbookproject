# Prison Book Project Database
 A workflow and data collection tool designed to track letters from incarcerated readers.

## Changelog
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

## Setup

### Create environment
1. Install [poetry](https://python-poetry.org/docs/#installation).
2. Create `.env` file (see `.env.example`). 
3. Activate virtual environment.
    - [optional] Install and use [direnv](https://direnv.net/) to make use of project `.envrc`.

### Set up database
1. Install `postgres` if needed.
2. Set up project database and postgres user. Values such as `database_name`, `project_user`, and `project_user_pw` must match the `DATABASE_URL` env var parameters.
```
CREATE DATABASE <database_name>;
CREATE ROLE <project_user> LOGIN PASSWORD '<project_user_pw>';
# GRANT ALL ON DATABASE <database_name> TO <project_user>;
\c <database_name>
GRANT USAGE, CREATE ON SCHEMA public to <project_user>;

```
3. From project root, run `./manage.py migrate`
4. From project root, run `./manage.py createsuperuser`

### Run server
Test connection and attempt to log in as the superuser created in the previous section: `./manage.py runserver`

### Set up fly.io connection
This section assumes you are connecting to an existing set of fly.io apps. If spinning up a new instance, you can use fly.io to take advantage of this project's existing `fly.toml` file or choose your own hosting platform.
1. Install [flyctl](https://fly.io/docs/flyctl/install/).
2. Run `fly apps list` and follow prompts to log in.
