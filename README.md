# Ninja Kitchen Sink

> Where the Ninjas wash their dishes.

This project aims to provide some comparison between [Django Ninja](https://django-ninja.dev/) and [Django Rest Framework](https://www.django-rest-framework.org/).

## Dev environment

You'll need [Direnv](https://direnv.net/) and [Uv](https://docs.astral.sh/uv/getting-started/installation/).

```sh
direnv allow
uv sync
pre-commit install --install-hooks
```

Useful commands:

```sh
# Create superuser to access the admin interface in http://localhost:8000/admin/
django createsuperuser --username=admin --email=admin@example.com

# Run the dev server
django runserver

# Run the tests
pytest
```
