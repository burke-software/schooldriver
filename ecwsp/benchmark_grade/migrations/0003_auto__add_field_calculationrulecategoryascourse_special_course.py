# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'CalculationRuleCategoryAsCourse.special_course'
        db.add_column(u'benchmark_grade_calculationrulecategoryascourse', 'special_course',
                      # There's not really a sane default value for this. MySQL accepted default=None,
                      # but SQLite does not.
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['schedule.Course']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'CalculationRuleCategoryAsCourse.special_course'
        db.delete_column(u'benchmark_grade_calculationrulecategoryascourse', 'special_course_id')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'benchmark_grade.aggregate': {
            'Meta': {'unique_together': "(('student', 'course', 'category', 'marking_period'),)", 'object_name': 'Aggregate'},
            'cached_substitution': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'cached_value': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['benchmark_grade.Category']", 'null': 'True', 'blank': 'True'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['schedule.Course']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manual_mark': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'marking_period': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['schedule.MarkingPeriod']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'points_possible': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.Student']", 'null': 'True', 'blank': 'True'})
        },
        u'benchmark_grade.aggregatetask': {
            'Meta': {'unique_together': "(('aggregate', 'task_id'),)", 'object_name': 'AggregateTask'},
            'aggregate': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['benchmark_grade.Aggregate']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'task_id': ('django.db.models.fields.CharField', [], {'max_length': '36'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        u'benchmark_grade.assignmenttype': {
            'Meta': {'object_name': 'AssignmentType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'benchmark_grade.calculationrule': {
            'Meta': {'object_name': 'CalculationRule'},
            'decimal_places': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'first_year_effective': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.SchoolYear']", 'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'points_possible': ('django.db.models.fields.DecimalField', [], {'default': '4', 'max_digits': '8', 'decimal_places': '2'})
        },
        u'benchmark_grade.calculationrulecategoryascourse': {
            'Meta': {'object_name': 'CalculationRuleCategoryAsCourse'},
            'calculation_rule': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'category_as_course_set'", 'to': u"orm['benchmark_grade.CalculationRule']"}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['benchmark_grade.Category']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_departments': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['schedule.Department']", 'null': 'True', 'blank': 'True'}),
            'special_course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['schedule.Course']"})
        },
        u'benchmark_grade.calculationrulepercoursecategory': {
            'Meta': {'object_name': 'CalculationRulePerCourseCategory'},
            'apply_to_departments': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['schedule.Department']", 'null': 'True', 'blank': 'True'}),
            'calculation_rule': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'per_course_category_set'", 'to': u"orm['benchmark_grade.CalculationRule']"}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['benchmark_grade.Category']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'weight': ('django.db.models.fields.DecimalField', [], {'default': '1', 'max_digits': '5', 'decimal_places': '4'})
        },
        u'benchmark_grade.calculationrulesubstitution': {
            'Meta': {'object_name': 'CalculationRuleSubstitution'},
            'apply_to_categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['benchmark_grade.Category']", 'null': 'True', 'blank': 'True'}),
            'apply_to_departments': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['schedule.Department']", 'null': 'True', 'blank': 'True'}),
            'calculate_as': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'calculation_rule': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'substitution_set'", 'to': u"orm['benchmark_grade.CalculationRule']"}),
            'display_as': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'flag_visually': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match_value': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'operator': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        },
        u'benchmark_grade.category': {
            'Meta': {'ordering': "['display_order']", 'object_name': 'Category'},
            'allow_multiple_demonstrations': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'demonstration_aggregation_method': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'display_in_gradebook': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'display_order': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'display_scale': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'display_symbol': ('django.db.models.fields.CharField', [], {'max_length': '7', 'null': 'True', 'blank': 'True'}),
            'fixed_granularity': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'fixed_points_possible': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'benchmark_grade.demonstration': {
            'Meta': {'object_name': 'Demonstration'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['benchmark_grade.Item']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'benchmark_grade.item': {
            'Meta': {'object_name': 'Item'},
            'assignment_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['benchmark_grade.AssignmentType']", 'null': 'True', 'blank': 'True'}),
            'benchmark': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['benchmarks.Benchmark']", 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['benchmark_grade.Category']"}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['schedule.Course']"}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marking_period': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['schedule.MarkingPeriod']", 'null': 'True', 'blank': 'True'}),
            'multiplier': ('django.db.models.fields.DecimalField', [], {'default': '1', 'max_digits': '8', 'decimal_places': '2'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'points_possible': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'})
        },
        u'benchmark_grade.mark': {
            'Meta': {'unique_together': "(('item', 'demonstration', 'student'),)", 'object_name': 'Mark'},
            'demonstration': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['benchmark_grade.Demonstration']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['benchmark_grade.Item']"}),
            'letter_grade': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'mark': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'normalized_mark': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.Student']"})
        },
        u'benchmarks.benchmark': {
            'Meta': {'ordering': "('number', 'name')", 'object_name': 'Benchmark'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'measurement_topics': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['benchmarks.MeasurementTopic']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '700'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.GradeLevel']", 'null': 'True', 'blank': 'True'})
        },
        u'benchmarks.department': {
            'Meta': {'object_name': 'Department'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'benchmarks.measurementtopic': {
            'Meta': {'ordering': "('department', 'name')", 'unique_together': "(('name', 'department'),)", 'object_name': 'MeasurementTopic'},
            'department': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['benchmarks.Department']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'schedule.course': {
            'Meta': {'object_name': 'Course'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'award_credits': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'credits': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'department': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['schedule.Department']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'enrollments': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['auth.User']", 'null': 'True', 'through': u"orm['schedule.CourseEnrollment']", 'blank': 'True'}),
            'fullname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'graded': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'homeroom': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_grade_submission': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.GradeLevel']", 'null': 'True', 'blank': 'True'}),
            'marking_period': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['schedule.MarkingPeriod']", 'symmetrical': 'False', 'blank': 'True'}),
            'periods': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['schedule.Period']", 'symmetrical': 'False', 'through': u"orm['schedule.CourseMeet']", 'blank': 'True'}),
            'secondary_teachers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'secondary_teachers'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['sis.Faculty']"}),
            'shortname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'teacher': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ateacher'", 'null': 'True', 'to': u"orm['sis.Faculty']"})
        },
        u'schedule.courseenrollment': {
            'Meta': {'unique_together': "(('course', 'user', 'role'),)", 'object_name': 'CourseEnrollment'},
            'attendance_note': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'cached_grade': ('django.db.models.fields.CharField', [], {'max_length': '8', 'blank': 'True'}),
            'cached_numeric_grade': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['schedule.Course']"}),
            'exclude_days': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['schedule.Day']", 'symmetrical': 'False', 'blank': 'True'}),
            'grade_recalculation_needed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'numeric_grade_recalculation_needed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'default': "'Student'", 'max_length': '255', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'year': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.GradeLevel']", 'null': 'True', 'blank': 'True'})
        },
        u'schedule.coursemeet': {
            'Meta': {'object_name': 'CourseMeet'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['schedule.Course']"}),
            'day': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['schedule.Location']", 'null': 'True', 'blank': 'True'}),
            'period': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['schedule.Period']"})
        },
        u'schedule.day': {
            'Meta': {'ordering': "('day',)", 'object_name': 'Day'},
            'day': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'schedule.department': {
            'Meta': {'ordering': "('order_rank', 'name')", 'object_name': 'Department'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'order_rank': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'schedule.location': {
            'Meta': {'object_name': 'Location'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'schedule.markingperiod': {
            'Meta': {'ordering': "('-start_date',)", 'object_name': 'MarkingPeriod'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'friday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'grades_due': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'monday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'saturday': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'school_days': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'school_year': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.SchoolYear']"}),
            'shortname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'show_reports': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'sunday': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'thursday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tuesday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'wednesday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'weight': ('django.db.models.fields.DecimalField', [], {'default': '1', 'max_digits': '5', 'decimal_places': '3'})
        },
        u'schedule.period': {
            'Meta': {'ordering': "('start_time',)", 'object_name': 'Period'},
            'end_time': ('django.db.models.fields.TimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'start_time': ('django.db.models.fields.TimeField', [], {})
        },
        u'sis.classyear': {
            'Meta': {'object_name': 'ClassYear'},
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'year': ('ecwsp.sis.models.IntegerRangeField', [], {'unique': 'True'})
        },
        u'sis.cohort': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Cohort'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_name': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'students': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sis.Student']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'sis.emergencycontact': {
            'Meta': {'ordering': "('primary_contact', 'lname')", 'object_name': 'EmergencyContact'},
            'city': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'emergency_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'fname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'mname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'primary_contact': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'relationship_to_student': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'state': ('localflavor.us.models.USStateField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'sync_schoolreach': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        u'sis.faculty': {
            'Meta': {'ordering': "('last_name', 'first_name')", 'object_name': 'Faculty', '_ormbases': [u'auth.User']},
            'ext': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'number': ('localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'blank': 'True'}),
            'teacher': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'sis.gradelevel': {
            'Meta': {'ordering': "('id',)", 'object_name': 'GradeLevel'},
            'id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150'})
        },
        u'sis.languagechoice': {
            'Meta': {'object_name': 'LanguageChoice'},
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso_code': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'sis.reasonleft': {
            'Meta': {'object_name': 'ReasonLeft'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'sis.schoolyear': {
            'Meta': {'ordering': "('-start_date',)", 'object_name': 'SchoolYear'},
            'active_year': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'benchmark_grade': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'grad_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        },
        u'sis.student': {
            'Meta': {'ordering': "('last_name', 'first_name')", 'object_name': 'Student', '_ormbases': [u'auth.User']},
            'alert': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'alt_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'bday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'cache_cohort': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'cache_cohorts'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['sis.Cohort']"}),
            'cached_gpa': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'class_of_year': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.ClassYear']", 'null': 'True', 'blank': 'True'}),
            'cohorts': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sis.Cohort']", 'symmetrical': 'False', 'blank': 'True'}),
            'date_dismissed': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'emergency_contacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sis.EmergencyContact']", 'symmetrical': 'False', 'blank': 'True'}),
            'family_access_users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'+'", 'blank': 'True', 'to': u"orm['auth.User']"}),
            'family_preferred_language': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['sis.LanguageChoice']", 'null': 'True', 'blank': 'True'}),
            'gpa_recalculation_needed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'grad_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'individual_education_program': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mname': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'parent_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'parent_guardian': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'pic': ('ecwsp.sis.thumbs.ImageWithThumbsField', [], {'blank': 'True', 'max_length': '100', 'null': 'True', 'sizes': '((70, 65), (530, 400))'}),
            'reason_left': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.ReasonLeft']", 'null': 'True', 'blank': 'True'}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'siblings': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sis.Student']", 'symmetrical': 'False', 'blank': 'True'}),
            'ssn': ('django.db.models.fields.CharField', [], {'max_length': '11', 'null': 'True', 'blank': 'True'}),
            'state': ('localflavor.us.models.USStateField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'unique_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'}),
            'year': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.GradeLevel']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        }
    }

    complete_apps = ['benchmark_grade']
