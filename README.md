# Ninja Kitchen Sink

> Where the Ninjas wash their dishes.

## Dev environment

You'll need [Direnv](https://direnv.net/) and [Uv](https://docs.astral.sh/uv/getting-started/installation/).

```sh
direnv allow
uv sync
pre-commit install --install-hooks
```

Run the dev server:

```sh
django runserver
```

Run the tests:

```sh
pytest
```
