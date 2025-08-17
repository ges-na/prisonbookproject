ARG PYTHON_VERSION=3.12-slim-bullseye

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN mkdir -p /app

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN pip3 install poetry==2.1.4
RUN poetry run true
ARG VIRTUAL_ENV=$(poetry env info --path)
ARG PATH=$VIRTUAL_ENV/bin:$PATH
RUN poetry env use 3.12

RUN poetry install

COPY . /app/

ENV DJANGO_SETTINGS_MODULE "src.prisonbookproject.settings_deployed"
ENV ALLOWED_HOSTS "*","127.0.0.1:8000","localhost","0.0.0.0"
ENV CSRF_TRUSTED_ORIGINS "https://prisonbookproject.fly.dev","https://ppbp-dev.fly.dev","http://127.0.0.1:8000","localhost"
ENV CORS_WHITELIST "https://prisonbookproject.fly.dev","https://ppbp-dev.fly.dev","http://127.0.0.1:8000"

EXPOSE 8000

# CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["sh", "-c", "poetry run python manage.py collectstatic --noinput && poetry run gunicorn --bind :8000 --workers 2 src.prisonbookproject.wsgi:application"]
