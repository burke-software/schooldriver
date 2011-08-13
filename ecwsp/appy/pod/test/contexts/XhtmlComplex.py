# -*- coding: utf-8 -*-
xhtmlInput = '''
<p>Te<b>s</b>t1 : <b>bold</b>, i<i>tal</i>ics, exponent<sup>34</sup>, sub<sub>45</sub>.</p>
<p>An <a href="http://www.google.com">hyperlink</a> to Google.</p>
<ol><li>Number list, item 1</li>
<ol><li>Sub-item 1</li><li>Sub-Item 2</li>
<ol><li>Sub-sub-item A</li><li>Sub-sub-item B <i>italic</i>.</li></ol>
</ol>
</ol>
<ul><li>A bullet</li>
<ul><li>A sub-bullet</li>
<ul><li>A sub-sub-bullet</li></ul>
<ol><li>A sub-sub number</li><li>Another.<br /></li></ol>
</ul>
</ul>
<h2>Heading<br /></h2>
Heading Blabla.<br />
<h3>SubHeading</h3>
Subheading blabla.<br />
'''
# I need a class.
class D:
    def getAt1(self):
        return xhtmlInput
dummy = D()
