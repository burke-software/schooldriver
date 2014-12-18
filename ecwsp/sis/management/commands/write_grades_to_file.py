from django.core.management.base import BaseCommand, CommandError
from ecwsp.grades.models import Grade
import os

class Command(BaseCommand):
    """This command writes grades to a file for use with the command
    restore_grades_from_file which restores these grades from that file"""

    help = 'write grades to file [../sis/management/commands/grades.txt]'

    def handle(self, *args, **options):
        course_sections = [3242]
        grades = Grade.objects.filter(course_section_id__in=course_sections)

        this_folder = os.path.dirname(os.path.realpath(__file__))
        output_file_path = this_folder + "/grades.txt"
        with open(output_file_path, "w") as f:
            for grade in grades:
                CS = grade.course_section.id
                if not grade.marking_period:
                    MP = None
                else:
                    MP = grade.marking_period.id
                Std = grade.student.id
                Grd = grade.grade
                Ovr = grade.override_final
                new_line = "%s,%s,%s,%s,%s\n" % (CS, MP, Std, Grd, Ovr)
                f.write(new_line)
