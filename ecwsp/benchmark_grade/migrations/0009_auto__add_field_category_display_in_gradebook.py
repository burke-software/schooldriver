# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Category.display_in_gradebook'
        db.add_column('benchmark_grade_category', 'display_in_gradebook',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Category.display_in_gradebook'
        db.delete_column('benchmark_grade_category', 'display_in_gradebook')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'benchmark_grade.aggregate': {
            'Meta': {'object_name': 'Aggregate'},
            'aggregate': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'aggregate_rel_+'", 'null': 'True', 'to': "orm['benchmark_grade.Aggregate']"}),
            'cachedValue': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['benchmark_grade.Category']", 'null': 'True', 'blank': 'True'}),
            'course': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['schedule.Course']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manualMark': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'points_possible': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'singleCategory': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'single_category'", 'null': 'True', 'to': "orm['benchmark_grade.Category']"}),
            'singleCourse': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'single_course'", 'null': 'True', 'to': "orm['schedule.Course']"}),
            'singleMarkingPeriod': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.MarkingPeriod']", 'null': 'True', 'blank': 'True'}),
            'singleStudent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'single_student'", 'null': 'True', 'to': "orm['sis.Student']"}),
            'student': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sis.Student']", 'null': 'True', 'blank': 'True'})
        },
        'benchmark_grade.assignmenttype': {
            'Meta': {'object_name': 'AssignmentType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'benchmark_grade.calculationrule': {
            'Meta': {'object_name': 'CalculationRule'},
            'decimal_places': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'first_year_effective': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.SchoolYear']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'points_possible': ('django.db.models.fields.DecimalField', [], {'default': '4', 'max_digits': '8', 'decimal_places': '2'})
        },
        'benchmark_grade.calculationrulecategoryascourse': {
            'Meta': {'object_name': 'CalculationRuleCategoryAsCourse'},
            'calculation_rule': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'category_as_course_set'", 'to': "orm['benchmark_grade.CalculationRule']"}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['benchmark_grade.Category']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_departments': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['schedule.Department']", 'null': 'True', 'blank': 'True'})
        },
        'benchmark_grade.calculationrulepercoursecategory': {
            'Meta': {'object_name': 'CalculationRulePerCourseCategory'},
            'apply_to_departments': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['schedule.Department']", 'null': 'True', 'blank': 'True'}),
            'calculation_rule': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'per_course_category_set'", 'to': "orm['benchmark_grade.CalculationRule']"}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['benchmark_grade.Category']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'weight': ('django.db.models.fields.DecimalField', [], {'default': '1', 'max_digits': '5', 'decimal_places': '4'})
        },
        'benchmark_grade.category': {
            'Meta': {'object_name': 'Category'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Course']", 'null': 'True', 'blank': 'True'}),
            'display_in_gradebook': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'weight': ('django.db.models.fields.DecimalField', [], {'default': '1', 'max_digits': '8', 'decimal_places': '2'})
        },
        'benchmark_grade.item': {
            'Meta': {'object_name': 'Item'},
            'assignment_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['benchmark_grade.AssignmentType']", 'null': 'True', 'blank': 'True'}),
            'benchmark': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['omr.Benchmark']", 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['benchmark_grade.Category']"}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Course']"}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'markingPeriod': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.MarkingPeriod']", 'null': 'True', 'blank': 'True'}),
            'multiplier': ('django.db.models.fields.DecimalField', [], {'default': '1', 'max_digits': '8', 'decimal_places': '2'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'points_possible': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'})
        },
        'benchmark_grade.mark': {
            'Meta': {'object_name': 'Mark'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'excused': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['benchmark_grade.Item']"}),
            'mark': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.Student']"})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'omr.benchmark': {
            'Meta': {'ordering': "('number', 'name')", 'unique_together': "(('number', 'name'),)", 'object_name': 'Benchmark'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'measurement_topics': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['omr.MeasurementTopic']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '700'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.GradeLevel']", 'null': 'True', 'blank': 'True'})
        },
        'omr.department': {
            'Meta': {'object_name': 'Department'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'omr.measurementtopic': {
            'Meta': {'ordering': "('department', 'name')", 'unique_together': "(('name', 'department'),)", 'object_name': 'MeasurementTopic'},
            'department': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['omr.Department']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '700'})
        },
        'schedule.course': {
            'Meta': {'object_name': 'Course'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'credits': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'department': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Department']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'enrollments': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sis.MdlUser']", 'null': 'True', 'through': "orm['schedule.CourseEnrollment']", 'blank': 'True'}),
            'fullname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'graded': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'homeroom': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_grade_submission': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.GradeLevel']", 'null': 'True', 'blank': 'True'}),
            'marking_period': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['schedule.MarkingPeriod']", 'symmetrical': 'False', 'blank': 'True'}),
            'periods': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['schedule.Period']", 'symmetrical': 'False', 'through': "orm['schedule.CourseMeet']", 'blank': 'True'}),
            'secondary_teachers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'secondary_teachers'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['sis.Faculty']"}),
            'shortname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'teacher': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ateacher'", 'null': 'True', 'to': "orm['sis.Faculty']"})
        },
        'schedule.courseenrollment': {
            'Meta': {'unique_together': "(('course', 'user', 'role'),)", 'object_name': 'CourseEnrollment'},
            'attendance_note': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Course']"}),
            'exclude_days': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['schedule.Day']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'default': "'Student'", 'max_length': '255', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.MdlUser']"}),
            'year': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.GradeLevel']", 'null': 'True', 'blank': 'True'})
        },
        'schedule.coursemeet': {
            'Meta': {'object_name': 'CourseMeet'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Course']"}),
            'day': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Location']", 'null': 'True', 'blank': 'True'}),
            'period': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Period']"})
        },
        'schedule.day': {
            'Meta': {'ordering': "('day',)", 'object_name': 'Day'},
            'day': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'schedule.department': {
            'Meta': {'ordering': "('order_rank', 'name')", 'object_name': 'Department'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'order_rank': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'schedule.location': {
            'Meta': {'object_name': 'Location'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'schedule.markingperiod': {
            'Meta': {'ordering': "('-start_date',)", 'object_name': 'MarkingPeriod'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'friday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'monday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'saturday': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'school_days': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'school_year': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.SchoolYear']"}),
            'shortname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'show_reports': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'sunday': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'thursday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tuesday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'wednesday': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'schedule.period': {
            'Meta': {'ordering': "('start_time',)", 'object_name': 'Period'},
            'end_time': ('django.db.models.fields.TimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'start_time': ('django.db.models.fields.TimeField', [], {})
        },
        'sis.classyear': {
            'Meta': {'object_name': 'ClassYear'},
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'year': ('ecwsp.sis.models.IntegerRangeField', [], {'unique': 'True'})
        },
        'sis.cohort': {
            'Meta': {'object_name': 'Cohort'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'students': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sis.Student']", 'null': 'True', 'db_table': "'sis_studentcohort'", 'blank': 'True'})
        },
        'sis.emergencycontact': {
            'Meta': {'ordering': "('primary_contact', 'emergency_only', 'lname')", 'object_name': 'EmergencyContact'},
            'city': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'emergency_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'fname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'mname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'primary_contact': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'relationship_to_student': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        'sis.faculty': {
            'Meta': {'ordering': "('lname', 'fname')", 'object_name': 'Faculty', '_ormbases': ['sis.MdlUser']},
            'alt_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'ext': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'mdluser_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sis.MdlUser']", 'unique': 'True', 'primary_key': 'True'}),
            'number': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'blank': 'True'}),
            'teacher': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'sis.gradelevel': {
            'Meta': {'ordering': "('id',)", 'object_name': 'GradeLevel'},
            'id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150'})
        },
        'sis.languagechoice': {
            'Meta': {'object_name': 'LanguageChoice'},
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso_code': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'sis.mdluser': {
            'Meta': {'ordering': "('lname', 'fname')", 'object_name': 'MdlUser'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '360', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'fname': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inactive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lname': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'sis.reasonleft': {
            'Meta': {'object_name': 'ReasonLeft'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'sis.schoolyear': {
            'Meta': {'ordering': "('-start_date',)", 'object_name': 'SchoolYear'},
            'active_year': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'benchmark_grade': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'grad_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        },
        'sis.student': {
            'Meta': {'ordering': "('lname', 'fname')", 'object_name': 'Student', '_ormbases': ['sis.MdlUser']},
            'alert': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'alt_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'bday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'cache_cohort': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'cache_cohorts'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['sis.Cohort']"}),
            'cache_gpa': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'class_of_year': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.ClassYear']", 'null': 'True', 'blank': 'True'}),
            'cohorts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sis.Cohort']", 'symmetrical': 'False', 'through': "orm['sis.StudentCohort']", 'blank': 'True'}),
            'date_dismissed': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'emergency_contacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sis.EmergencyContact']", 'symmetrical': 'False', 'blank': 'True'}),
            'family_access_users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'}),
            'family_preferred_language': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['sis.LanguageChoice']", 'null': 'True', 'blank': 'True'}),
            'grad_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'individual_education_program': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mdluser_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sis.MdlUser']", 'unique': 'True', 'primary_key': 'True'}),
            'mname': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'parent_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'parent_guardian': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'pic': ('ecwsp.sis.thumbs.ImageWithThumbsField', [], {'blank': 'True', 'max_length': '100', 'null': 'True', 'sizes': '((70, 65), (530, 400))'}),
            'reason_left': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.ReasonLeft']", 'null': 'True', 'blank': 'True'}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'siblings': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sis.Student']", 'symmetrical': 'False', 'blank': 'True'}),
            'ssn': ('django.db.models.fields.CharField', [], {'max_length': '11', 'null': 'True', 'blank': 'True'}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'unique_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.GradeLevel']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        'sis.studentcohort': {
            'Meta': {'object_name': 'StudentCohort'},
            'cohort': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.Cohort']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.Student']"})
        }
    }

    complete_apps = ['benchmark_grade']