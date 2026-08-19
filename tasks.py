"""Dogfoods the same quality tasks every template consumer gets — see README.md."""

from invoke import Collection
from repo_tasks import quality

ns = Collection.from_module(quality)
