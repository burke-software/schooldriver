.. _develop:

Developing django-sis
=====================

Cache and grade calculations
----------------------------

1. All cached datbaase fields must use django-cached-field.
2. Models that can invalidate another models cache must have a invalidate_cache method

See Chart https://docs.google.com/drawings/d/1RWuOcglD8BvkDeSASJA2yH4wXvtAezdqAV0xMdGWqYU/edit?usp=sharing
Discussion Doc https://docs.google.com/document/d/1lZAiPqKpZe_Ah9nCL5iBb5z3dpvjqWBZxLQcuFsDG-Y/edit?usp=sharing
