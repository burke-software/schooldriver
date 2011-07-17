# -*- coding: utf-8 -*-  

import sys
from ecwsp.work_study.models import Company, Contact, Student
sys.path.append( '../' )
from PyRTF import *
import unicodedata

def OpenFile( name ) :
        return file( '/var/www/tmp/%s.rtf' % name, 'w' )

class orGen:
    def chaperone(self):
        doc     = Document()
        ss      = doc.StyleSheet
        section = Section()
        doc.Sections.append( section )
        bigBold = TextPS( size=34, font=ss.Fonts.TimesNewRoman )
        bold = TextPS( bold=True, font=ss.Fonts.TimesNewRoman )
        normal = TextPS(size= 26, font=ss.Fonts.TimesNewRoman )
        
            
        for comp in Company.objects.filter():
            p = Paragraph()
            p.append(Text( "Instructions for Chaperones:", bigBold))
            section.append( p )

            p = Paragraph()
            p.append(Text( str(comp.companyName),bigBold))
            section.append(p)
            
            p = Paragraph()
            p.append(Text(str(comp.address),normal))
            section.append(p)
            
            p = Paragraph()
            p.append(Text( str(comp.city + ", " + comp.state + " " + comp.zip),normal))
            section.append(p)
            
            section.append("")
            
            for con in Contact.objects.filter(placement__id=comp.id):
                p = Paragraph()
                p.append(Text( str("Contact: " + str(con) + " - " + str(con.phone)),normal))
                section.append(p)
            
            section.append("")
            
            p = Paragraph()
            p.append(Text("Meeting Time: ", bold))
            p.append(Text("Teachers should plan to be at Cristo Rey 1 hour before the meeting time.  Students will meet teachers 45 minutes before the meeting time.  Make sure everyone has valid ID before you leave Cristo Rey!", normal))
            section.append(p)
            
            section.append("")
            
            p = Paragraph()
            p.append(TEXT( "Students:", underline=True, font=ss.Fonts.TimesNewRoman))
            section.append(p)
            
            for stu in Student.objects.filter(placement__id=comp.id):
                sname = str(stu)
                sname = unicode( sname, "utf-8" )
                sname = unicodedata.normalize('NFKD', sname).encode('ascii','ignore')
                p = Paragraph()
                p.append(Text(sname,normal))
                section.append(p)
            
            section.append("")
            
            p = Paragraph()
            try:
                p.append(Text( "Directions to: " + str(comp.directionsTo),normal))
            except :
                p.append(Text( str("Error"),normal))
            section.append(p)
            
            section.append("")
            
            p = Paragraph()
            try:
                p.append(Text( "Pickup Location: " + str(comp.directionsPickup),normal))
            except: 
                 p.append(Text( str("Error"),normal))
            section.append(p)
                    
            section.append("")
                    
            p = Paragraph( )
            p.append(Text('-Bring Student(s) back to Cristo Rey High School after the Orientation is complete.  If you have any problems contact David Burke at 717 676 2133 or Kyle Leliaert at 347 582 6175.  Thanks!',normal))
            section.append( p )
            
            p = Paragraph( ss.ParagraphStyles.Normal, ParagraphPS().SetPageBreakBefore( True ) )
            p.append('')
            section.append( p )
                            
        DR = Renderer()

        doc1 = doc
        DR.Write( doc1, OpenFile( 'orientation_chap' ) )
    
    def makeMaps(self) :
        doc     = Document()
        ss      = doc.StyleSheet
        section = Section()
        doc.Sections.append( section )
        bigBold = TextPS( size=48, font=ss.Fonts.TimesNewRoman )
        bold = TextPS( bold=True, font=ss.Fonts.TimesNewRoman )
        normal = TextPS(font=ss.Fonts.TimesNewRoman )
        
            
        for comp in Company.objects.filter():
            p = Paragraph()
            p.append(Text( "JOB ASSIGNMENT:", bigBold))
            section.append( p )

            p = Paragraph()
            p.append(Text( str(comp.companyName),bigBold))
            section.append(p)
            
            section.append("")
            
            p = Paragraph()
            p.append(TEXT( "Team:", underline=True, font=ss.Fonts.TimesNewRoman))
            section.append(p)
            
            for stu in Student.objects.filter(placement__id=comp.id):
                sname = str(stu.get_day_display()) + ": " + str(stu)
                sname = unicode( sname, "utf-8" )
                sname = unicodedata.normalize('NFKD', sname).encode('ascii','ignore')
                p = Paragraph()
                p.append(Text(sname,normal))
                section.append(p)
            
            section.append("")
            
            p = Paragraph()
            p.append(Text("ORIENTATION MEETING: ", bold))
            p.append(Text("Arrive/ Be Ready at  Cristo Rey on ", normal))
            section.append(p)
                
            section.append("")
            
            p = Paragraph()
            p.append(Text( "NOTE: BRING THE FOLLOWING INFORMATION TO ORIENTATION MEETING:",bigBold))
            section.append(p)
            
            p = Paragraph()
            p.append(Text( "1. PICTURE ID",bigBold))
            section.append(p)
                    
            p = Paragraph( )
            p.append(Text('2. SOCIAL SECURITY NUMBER',bigBold))
            section.append( p )
            
            p = Paragraph( )
            p.append(Text('3. PERSONAL-HOME INFORMATION',bigBold))
            section.append( p )
            
            p = Paragraph( )
            p.append(Text('4. ADDRESS INCLUDING ZIP CODE',bigBold))
            section.append( p )
            
            p = Paragraph( )
            p.append(Text('5. PHONE NUMBER',bigBold))
            section.append( p )
            
            p = Paragraph( ss.ParagraphStyles.Normal, ParagraphPS().SetPageBreakBefore( True ) )
            p.append('')
            section.append( p )
                            
        DR = Renderer()

        doc1 = doc
        DR.Write( doc1, OpenFile( 'orientation' ) )
