.. _develop:

Developing django-sis
=====================

Cache and grade calculations
----------------------------

1. All cached datbaase fields must use django-cached-field.
2. Models that can invalidate another models cache must have a invalidate_cache method

See Chart https://docs.google.com/drawings/d/1RWuOcglD8BvkDeSASJA2yH4wXvtAezdqAV0xMdGWqYU/edit?usp=sharing
Discussion Doc https://docs.google.com/document/d/1lZAiPqKpZe_Ah9nCL5iBb5z3dpvjqWBZxLQcuFsDG-Y/edit?usp=sharing


School specific features
-------------------------

.. admonition:: A school wants some odd feature but it should be off by default. What do I do?

Settings should go in constance-config_. Help text and a sane default is required. 

.. _constance-config : ../django_sis/settings.py#L439

Prefix names when multiple settings are used. For example LDAP_USERNAME and LDAP_PASSWORD.

In the future settings will be given custom interfaces. The only way to edit constance now is in 
/admin -> Constance -> Config

Unit tests should added to confirm school specific features work. For example a setting that changes GPA should
include a unit test that verifies that when the setting is enabled - the GPA is affected as expected. Include this
unit test time in any paid estimates as a required part of the job.
