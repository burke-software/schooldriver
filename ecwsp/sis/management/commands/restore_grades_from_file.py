from django.core.management.base import BaseCommand, CommandError
from ecwsp.grades.models import Grade
import os
from decimal import Decimal
from django.db import transaction

class Command(BaseCommand):
    """read a raw text file containing grade data that has been deleted from
    the database and restore that data. We expect each line of the grade.txt 
    file to be in the following format: 

    CourseSectionID,MarkingPeriodID,StudentID,GradeDecimal,OverrideFinal

    Note: MarkingPeriodID and GradeDecimal might be None

    For example:

    3356,31,567,None,False
    3356,None,567,100.00,True
    3384,31,567,None,False
    3384,None,567,100.00,True
    3388,31,567,None,False
    3388,None,567,92.49,True
    ...


    on multi-tenant you should run using (according to the schema NAME)

    ( ... ) manage.py tenant_command restore_grades_from_file --schema=NAME

    """

    help = 'restore grades from file [../sis/management/commands/grades.txt]'

    def handle(self, *args, **options):
        this_folder = os.path.dirname(os.path.realpath(__file__))
        output_file_path = this_folder + "/grades.txt"
        lines = []
        with open(output_file_path, "r") as f:
            for line in f:
                line = line.strip('\n')
                lines.append(line)

        with transaction.atomic():
            new_grades = []
            for line in lines:
                grade_data = line.split(',')
                course_section_id = int(grade_data[0])

                if grade_data[1] == "None":
                    marking_period_id = None
                else:
                    marking_period_id = int(grade_data[1])

                student_id = int(grade_data[2])

                if grade_data[3] == "None":
                    grade_decimal = None
                else:
                    grade_decimal = Decimal(grade_data[3])

                if grade_data[4] == "False":
                    override_final = False
                else:
                    override_final = True

                # the filter below should only return 1 response since
                # the combo of section, student, and period is guaranteed
                # to be unique in our db. We could just use a get_or_create
                # but the get() and the save() each time takes forver
                num_updated = Grade.objects.filter(
                    course_section_id = course_section_id,
                    marking_period_id = marking_period_id,
                    student_id = student_id
                ).update(
                    override_final = override_final, 
                    grade=grade_decimal
                    )
                if num_updated == 0:
                    # the grade didn't exist, so the update above did nothing,
                    # let's just create a new grade and save it at the end
                    # using the bulk_create method which is much faster
                    # than calling save() each time
                    new_grade = Grade(
                            course_section_id = course_section_id,
                            marking_period_id = marking_period_id,
                            student_id = student_id,
                            grade = grade_decimal,
                            override_final = override_final,
                        )
                    new_grades.append(new_grade)

            Grade.objects.bulk_create(new_grades)

            


