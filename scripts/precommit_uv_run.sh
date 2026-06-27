#!/bin/bash
# Wrapper script for pre-commit hooks to support both shared/monorepo (Profile A)
# and standalone (Profile B) environments.
if [ -n "$VIRTUAL_ENV" ]; then
  exec uv run --active "$@"
else
  exec uv run "$@"
fi
