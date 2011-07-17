# -*- coding: utf-8 -*-  
# Generate a .rtf document of directions to a placement including a map.

from ecwsp.work_study.models import WorkTeam, Contact, PickupLocation, Student
from ecwsp.administration.models import Configuration
#sys.path.append( '../' )
from PyRTF import *
from django.http import HttpResponse
from django.conf import settings
import unicodedata
import sys

def strip_accents(s):
   return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')).encode('utf-8')

def genPara(text, ss):
        normal = TextPS(size= 20, font=ss.Fonts.TimesNewRoman )   
        para_props = ParagraphPS( space_before = 0, space_after = 0)
        p = Paragraph(ss.ParagraphStyles.Normal, para_props)
        p.append(Text( text, normal))
        return p

class PersonalityReport:
    def make_report(self) :
        doc     = Document()
        ss      = doc.StyleSheet
        section = Section()
        doc.Sections.append( section )
        
        normal = TextPS(size= 20, font=ss.Fonts.TimesNewRoman )   
        para_props = ParagraphPS( space_before = 0, space_after = 0)
        
        section.Header.append(Image(settings.MEDIA_ROOT + "/images/header_paper.jpg"))
        
        students = Student.objects.all().order_by('year')
        first = True
        for student in students:
            try:
                if first:
                    p = Paragraph( ss.ParagraphStyles.Normal)
                    first = False
                else:
                    p = Paragraph( ss.ParagraphStyles.Normal, ParagraphPropertySet().SetPageBreakBefore( True ) )
                p.append("Name: " + strip_accents(student.fname) + " " + strip_accents(student.lname) )
                section.append(p)
                p = Paragraph( ss.ParagraphStyles.Normal)
                p.append("Grade:" + str(student.year))
                section.append(p)
                p = Paragraph( ss.ParagraphStyles.Normal)
                p.append("Myers-Briggs Type Indicator")
                section.append(p)
                p = Paragraph( ss.ParagraphStyles.Normal)
                p.append("-MBTI assessment is a questionnaire designed to measure psychological preferences in how people perceive the world and make decisions.  We had each student complete this assessment.  You can learn more about MBTI on the attachment that follows.")
                section.append(p)
                p = Paragraph( ss.ParagraphStyles.Normal)
                p.append("Personality Type: " + str(student.personality_Type))
                section.append(p)
                p = Paragraph( ss.ParagraphStyles.Normal)
                p.append("Type Description: ")
                if student.personality_Type:
                    p.append(str(student.personality_Type.description))
                section.append(p)
                p = Paragraph( ss.ParagraphStyles.Normal)
                p.append("Student Personality Traits: We surveyed every student to find out the types of things they like to do.  These preferences are categorised across different personality traits.  The following statements most closely reflect the learning tasks that your student worker finds appealing.  The handout we gave to the students is attached.")
                section.append(p)
                
                for trait in student.handout33.all():
                    p = Paragraph( ss.ParagraphStyles.Normal)
                    p.append(str(trait))
                    section.append(p)
            
            except:
                print >> sys.stderr, "Error: Personality report didn't work" + str(sys.exc_info()[0])
            
        DR = Renderer()

        doc1 = doc
            
        response = HttpResponse(mimetype="application/rtf")
        response['Content-Disposition'] = 'attachment; filename=%s' % "personality.rtf"
        #self.wb.save(response)
        DR.Write( doc1, response )
        return response

class mapsGen:
    def makeMaps(self, sort_team=False) :
        doc     = Document()
        ss      = doc.StyleSheet
        section = Section()
        doc.Sections.append( section )
        
        normal = TextPS(size= 20, font=ss.Fonts.TimesNewRoman )   
        para_props = ParagraphPS( space_before = 0, space_after = 0)
        
        #get phone numbers or create config object if needed
        try:
            numbers = Configuration.objects.get(name="CWSP numbers")
        except:
            # doesn't exist, so make it because we need it.
            numbersConf = Configuration(name="CWSP numbers", value="names and numbers of CWSP staff goes here")
            numbersConf.save()
            numbers = Configuration.objects.get(name="CWSP numbers")
        try:
            schoolNumber = Configuration.objects.get(name="School number")
        except:
            # doesn't exist, so make it because we need it.
            numbersConf = Configuration(name="School number", value="school phone number goes here.")
            numbersConf.save()
            schoolNumber = Configuration.objects.get(name="School number")
        
        section.Footer.append( genPara("Don't Get Lost! \n\nProtocol", ss) )
        p = genPara("Not sure where you are or how to get to where you're supposed to be? Follow these steps:", ss)
        section.Footer.append( p )
        p = genPara("1.  Use your map, including the street address and directions written on it; if you still can't figure it out...", ss)
        section.Footer.append( p )
        p = genPara("2.  Ask for help from someone official: a police officer, a store owner, a security guard or the front desk staff at an office building; if you can't still find where you're going...", ss)
        section.Footer.append( p )
        p = genPara("3.  Call " + str(numbers.value) + "; you may use your cell phone, or go into an office building and explain to security your situation and ask if you can use a phone...", ss)
        section.Footer.append( p )
        p = genPara("4.  Finally, as a last resort, you also have the phone number for your company on this sheet; you may call your office or call the school (" + str(schoolNumber.value) + ") or call your family", ss)
        section.Footer.append( p )
        p = genPara( "BUT ALWAYS let the CWSP staff know where you are!", ss)
        section.Footer.append( p )
        
        if sort_team:
            companies = WorkTeam.objects.all().order_by('pickup_location')
        else:
            companies = WorkTeam.objects.all()
        for comp in companies:
            if comp.is_active() == "Active":
                try:
                    table = Table( TabPS.DEFAULT_WIDTH * 6,
                                TabPS.DEFAULT_WIDTH * 7)
                    p = genPara(str(comp.team_name), ss)
                    c1 = Cell( p )
                    c1.append (genPara(  str(comp.address), ss ) )
                    c1.append (genPara(  str(comp.city) + ", " + str(comp.state) + " " +  str(comp.zip), ss ) )
                    for con in Contact.objects.filter(workteam__id = comp.id):
                        c1.append (genPara(str(con.fname + " " + con.lname), ss ) )
                        c1.append (genPara(str(con.phone), ss ) )
                    try:
                        p = genPara( 'To placement: ' + str(comp.directions_to), ss)
                        c2 = Cell( p )
                        p = genPara('Pickup: ' + str(comp.directions_pickup) + '  ' + str(comp.pickup_location.directions), ss)
                        c2.append(p)
                    except:
                        c2 = Cell( Paragraph( 'ERROR' ) )
                    table.AddRow( c1, c2 )
                    section.append( table )
                    
                    table = Table( TabPS.DEFAULT_WIDTH * 13)
                    txt = ""
                    try:
                        mapFile = unicode(comp.map.path)
                        txt = mapFile
                        c1 = Cell( Paragraph( Image(mapFile)))
                    except:
                        c1 = Cell( Paragraph(txt))
                    table.AddRow( c1 )
                    section.append( table )
                    
                    p = Paragraph( ss.ParagraphStyles.Normal, ParagraphPS().SetPageBreakBefore( True ) )
                    p.append('')
                    section.append( p )
                except:
                    print >> sys.stderr, "Error: Maps didn't work"
        DR = Renderer()
        response = HttpResponse(mimetype="application/rtf")
        response['Content-Disposition'] = 'attachment; filename=%s' % "maps.rtf"
        DR.Write( doc, response )
        return response
