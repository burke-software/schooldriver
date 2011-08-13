# -*- coding: utf-8 -*-
# I need a class.
class D:
    def getAt1(self):
        return '''
<p>Notifia</p>
<ol>
  <li>Een</li>
  <li>Een</li>
  <li>Een</li>
  <li class="podItemKeepWithNext">Keep with next, without style mapping.</li>
  <li>Een</li>
  <li>Een</li>
  <li>Een</li>
  <li>Een</li>
  <li>Een</li>
  <li>Een</li>
  <li>Een</li>
  <ul><li class="pmItemKeepWithNext">This one has 'keep with next'</li>
        <li>Hello</li>
          <ol><li>aaaaaaaaaa aaaaaaaaaaaaaa</li>
              <li>aaaaaaaaaa aaaaaaaaaaaaaa</li>
              <li>aaaaaaaaaa aaaaaaaaaaaaaa</li>
              <li class="pmItemKeepWithNext">This one has 'keep with next'</li>
          </ol>
  </ul>
  <li>Een</li>
  <li>Een</li>
  <li>Een</li>
  <li>Een</li>
  <li>Een</li>
  <li>Een</li>
  <li class="pmItemKeepWithNext">This one has 'keep with next'</li>
</ol>
<ul>
  <li>Un</li>
  <li>Deux</li>
  <li>Trois</li>
  <li>Quatre</li>
  <li class="pmItemKeepWithNext">VCinq (this one has 'keep with next')</li>
  <li class="pmItemKeepWithNext">Six (this one has 'keep with next')</li>
  <li class="pmItemKeepWithNext">Sept (this one has 'keep with next')</li>
</ul>'''
dummy = D()
