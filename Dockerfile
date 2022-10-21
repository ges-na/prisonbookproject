ARG PYTHON_VERSION=3.10-slim-buster

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN mkdir -p /app

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN pip3 install poetry

RUN poetry install

COPY . /app/

ENV DJANGO_SETTINGS_MODULE "prisonbookproject.settings_deployed"
ENV ALLOWED_HOSTS "*","127.0.0.1:8000","localhost","0.0.0.0"
ENV CSRF_TRUSTED_ORIGINS "https://prisonbookproject.fly.dev","http://127.0.0.1:8000","localhost"
ENV CORS_WHITELIST "https://prisonbookproject.fly.dev","http://127.0.0.1:8000"

EXPOSE 8000

# CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["sh", "-c", "poetry run python manage.py collectstatic --noinput && poetry run gunicorn --bind :8000 --workers 2 prisonbookproject.wsgi:application"]
