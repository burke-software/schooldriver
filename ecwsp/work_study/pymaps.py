"""

*    Pymaps 0.9 
*    Copyright (C) 2007  Ashley Camba <stuff4ash@gmail.com> http://xthought.org
*
*    This program is free software; you can redistribute it and/or modify
*    it under the terms of the GNU General Public License as published by
*    the Free Software Foundation; either version 2 of the License, or
*    (at your option) any later version.
*
*    This program is distributed in the hope that it will be useful,
*    but WITHOUT ANY WARRANTY; without even the implied warranty of
*    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*    GNU General Public License for more details.
*
*    You should have received a copy of the GNU General Public License
*    along with this program; if not, write to the Free Software
*    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

Changes by Bill (not a javascript programmer@) Luitje 29 July 2009
* fixed default parameter use for lists
* fixed icon javascript generation. works!
* updated example code

Some getting started info here:
http://lycos.dropcode.net/gregarius/Lonely_Code/2008/12/04/Google_Maps_and_Django

@ and not much of a python programmer either.
"""
class Icon:
    '''Get/make marker icons at http://mapki.com/index.php?title=Icon_Image_Sets'''
    def __init__(self,id='icon'):
        self.id = id
        self.image = ""     #uses default Google Maps icon
        self.shadow = ""
##        self.image = "http://labs.google.com/ridefinder/images/mm_20_blue.png"
##        self.shadow = "http://labs.google.com/ridefinder/images/mm_20_shadow.png"
        self.iconSize = (12, 20)    # these settings match above icons
        self.shadowSize = (22, 20)
        self.iconAnchor = (6, 20)
        self.infoWindowAnchor = (5, 1)

        
class Map:
    def __init__(self,id="map",pointlist=None):
        self.id       = id    # div id        
        self.width    = "500px"  # map div width
        self.height   = "300px"  # map div height
        self.center   = (0,0)     # center map latitude coordinate
        self.zoom        = "1"   # zoom level
        self.navcontrols  =   True   # show google map navigation controls
        self.mapcontrols  =   True   # show toogle map type (sat/map/hybrid) controls
        if pointlist == None:
            self.points = []   # empty point list
        else:
            self.points = pointlist   # supplied point list
    
    def __str__(self):
        return self.id
        
    
    def setpoint(self, point):
        """ Add a point (lat,long,html,icon) """
        self.points.append(point)

class PyMap:
    """
    Python wrapper class for Google Maps API.
    """
    
    def __str__(self):
        return "Pymap"
    
    def __init__(self, key=None, maplist=None, iconlist=None):
        """ Default values """
        self.key      = "ABQIAAAAQQRAsOk3uqvy3Hwwo4CclBTrVPfEE8Ms0qPwyRfPn-DOTlpaLBTvTHRCdf2V6KbzW7PZFYLT8wFD0A"      # set your google key
        if maplist == None:
            self.maps = [Map()]
        else:
            self.maps = maplist
        if iconlist == None:
            self.icons = [Icon()]
        else:
            self.icons = iconlist
    
    def addicon(self,icon):
        self.icons.append(icon)
        
    def _navcontroljs(self,map):
        """ Returns the javascript for google maps control"""    
        if map.navcontrols:
            return  "           %s.gmap.addControl(new GSmallMapControl());\n" % (map.id)
        else:
            return ""    
    
    
    def _mapcontroljs(self,map):
        """ Returns the javascript for google maps control"""    
        if map.mapcontrols:
            return  "           %s.gmap.addControl(new GMapTypeControl());\n" % (map.id)
        else:
            return ""     
    
    
    def _showdivhtml(self,map):
        """ Returns html for dislaying map """
        html = """\n<div id=\"%s\">\n</div>\n""" % (map.id)
        return html
    
    def _point_hack(self, points):
        count = 1
        
        for item in points:
            open = str(item).replace("(", "[")
            open = open.replace(")", "]")
        
        return open
    
    
    def _mapjs(self,map):
        js = "%s_points = %s;\n" % (map.id,map.points)
        
        js = js.replace("(", "[")
        js = js.replace(")", "]")
        js = js.replace("u'", "'")
        js = js.replace("''","")    #python forces you to enter something in a list, so we remove it here
##        js = js.replace("'icon'", "icon")
        for icon  in self.icons:
            js = js.replace("'"+icon.id+"'",icon.id)
        js +=   """             var %s = new Map('%s',%s_points,%s,%s,%s);
        \n\n%s\n%s""" % (map.id,map.id,map.id,map.center[0],map.center[1],map.zoom, self._mapcontroljs(map), self._navcontroljs(map))
        return js
    
    
    
    def _iconjs(self,icon):
        js = """ 
                var %s = new GIcon(); 
                %s.image = "%s";
                %s.shadow = "%s";
                %s.iconSize = new GSize(%s, %s);
                %s.shadowSize = new GSize(%s, %s);
                %s.iconAnchor = new GPoint(%s, %s);
                %s.infoWindowAnchor = new GPoint(%s, %s);
        """ % (icon.id, icon.id, icon.image, icon.id, icon.shadow, icon.id, icon.iconSize[0],icon.iconSize[1],icon.id, icon.shadowSize[0], icon.shadowSize[1], icon.id, icon.iconAnchor[0],icon.iconAnchor[1], icon.id, icon.infoWindowAnchor[0], icon.infoWindowAnchor[1])
        return js
     
    def _buildicons(self):
        js = ""
        if (len(self.icons) > 0):
            for i in self.icons:
               js = js + self._iconjs(i)    
        return js
    
    def _buildmaps(self):
        js = ""
        for i in self.maps:
            js = js + self._mapjs(i)+'\n'
        return js

    def pymapjs(self):
        """ Returns complete javacript for rendering map """
        
        self.js = """\n<script src=\"http://maps.google.com/maps?file=api&amp;v=2&amp;key=%s\" type="text/javascript"></script>
        <script type="text/javascript">
        //<![CDATA[
        function load() {
            if (GBrowserIsCompatible()) {
                
            
            function Point(lat,long,html,icon) {
                  this.gpoint = new GMarker(new GLatLng(lat,long),icon);
                  this.html = html;
                  
               }               
               
               
               function Map(id,points,lat,long,zoom) {
                  this.id = id;
                  this.points = points;
                  this.gmap = new GMap2(document.getElementById(this.id));
                  this.gmap.setCenter(new GLatLng(lat, long), zoom);
                  this.markerlist = markerlist;
                  this.addmarker = addmarker;
                  this.array2points = array2points;
                   
                  function markerlist(array) {
                     for (var i in array) {
                        this.addmarker(array[i]);
                     }
                  }
                  
                  function array2points(map_points) {            
                      for (var i in map_points) {  
                        points[i] = new Point(map_points[i][0],map_points[i][1],map_points[i][2],map_points[i][3]);         }
                      return points;   
                    }                  
                  
                  function addmarker(point) {
                     if (point.html) {
                       GEvent.addListener(point.gpoint, "click", function() { // change click to mouseover or other mouse action
                           point.gpoint.openInfoWindowHtml(point.html);
                        
                       });
                       
                     }
                     this.gmap.addOverlay(point.gpoint);  
                  }
                  this.points = array2points(this.points);
                  this.markerlist(this.points);
            }  
                    %s
                    %s
            }
        }
        //]]>
        </script>
        
        
        """ % (self.key, self._buildicons(),self._buildmaps())
        return self.js 
    
    
        
    def showhtml(self):
        """returns a complete html page with a map"""
        
        self.html = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
    <title></title>
    %s
  </head>

  <body onload="load()" onunload="GUnload()">
    <div id="map" style="width: 1000px; height: 600px"></div>
  </body>
</html>
""" % (self.pymapjs())
        return self.html


if __name__ == "__main__":
    import sys
    
    g = PyMap()                         # creates an icon & map by default
    icon2 = Icon('icon2')               # create an additional icon
    icon2.image = "http://labs.google.com/ridefinder/images/mm_20_blue.png" # for testing only!
    icon2.shadow = "http://labs.google.com/ridefinder/images/mm_20_shadow.png" # do not hotlink from your web page!
    g.addicon(icon2)
    g.key = "ABQIAAAAQQRAsOk3uqvy3Hwwo4CclBTrVPfEE8Ms0qPwyRfPn-DOTlpaLBTvTHRCdf2V6KbzW7PZFYLT8wFD0A" # you will get your own key
    g.maps[0].zoom = 5
    q = [1,1]                           # create a marker with the defaults
    r = [2,2,'','icon2']                # icon2.id, specify the icon but no text
    s = [3,3,'hello, <u>world</u>']     # don't specify an icon & get the default
    g.maps[0].setpoint(q)               # add the points to the map
    g.maps[0].setpoint(r)
    g.maps[0].setpoint(s)
    
    open('test.htm','wb').write(g.showhtml())   # generate test file
