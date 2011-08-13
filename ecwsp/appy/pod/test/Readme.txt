Here you will find some ODT documents that are POD templates.

A POD template is a standard ODT file, where:
 - notes are used to insert Python-based code for telling POD to render
   a portion of the document zero, one or more times ("if" and "for" statements);
 - text insertions in "track changes" mode are interpreted as Python expressions.

When you run the Tester.py program with one of those ODT files as unique parameter
(ie "python Tester.py ForCellOnlyOne.odt"), you get a result.odt file which is the
result of executing the template with a bunch of Python objects. The "tests" dictionary
defined in Tester.py contains the objects that are given to each POD ODT template
contained in this folder.

Opening the templates with OpenOffice (2.0 or higher), running Tester.py on it and
checking the result in result.odt is probably the quickest way to have a good idea
of what appy.pod can make for you !
