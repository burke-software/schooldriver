# -*- coding: utf-8 -*-
xhtmlInput = '''
<p>Table test.</p>
<p>
<table class="plain">
<tbody>
<tr>
<td>Table 1 <br /></td>
<td colspan="2">aaaaa<br /></td>
</tr>
<tr>
<td>zzz <br /></td>
<td>
  <table>
    <tr>
      <td>SubTableA</td>
      <td>SubTableB</td>
    </tr>
    <tr>
      <td>SubTableC</td>
      <td>SubTableD</td>
    </tr>
  </table>
</td>
<td><b>Hello</b> blabla<table><tr><td>SubTableOneRowOneColumn</td></tr></table></td>
</tr>
<tr>
<td><p>Within a <b>para</b>graph</p></td>
<td><b>Hello</b> non bold</td>
<td>Hello <b>bold</b> not bold</td>
</tr>
</tbody>
</table>
</p>
<br />'''
