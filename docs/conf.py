# -*- coding: utf-8 -*-
import sys, os
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.todo']
todo_include_todos = True

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

project = u'Django School Information System'
copyright = u'2013, Burke Software'

# The short X.Y version.
#version = '2.4.4'
# The full version, including alpha/beta/rc tags.
#release = '2.4.4'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'default'

# Add any paths that contain custom themes here, relative to this directory.
html_theme_path = ['.']

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Output file base name for HTML help builder.
htmlhelp_basename = ''

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
#latex_documents = [
#  ('index', '', u'',
#   u'', 'manual'),
#]

# -- Options for manual page output --------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
#man_pages = [
#    ('index', '', u'',
#     [u''], 1)
#]
