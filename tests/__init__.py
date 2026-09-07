"""Test suite for scaffoldapy.

A package, not a bare directory: pytest recommends packaging tests under the `prepend` import mode
this family uses, and it is what lets `support.py` be imported as `tests.support` — by namespace,
rather than by sitting at the front of `sys.path` where any module named `support` would shadow it.
The shipped pyrightconfig.json's `extraPaths` is the half that makes basedpyright resolve it, and
the shipped ruff.toml's `banned-api` entry for `src` guards the second import route that opens.

This is scaffoldapy's own suite, not the template's: `template/tests/` is a separate tree with its
own layout question, and nothing here is copied into a generated repo.
"""
