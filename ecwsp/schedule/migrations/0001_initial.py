# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MarkingPeriod'
        db.create_table('schedule_markingperiod', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('shortname', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')()),
            ('school_year', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.SchoolYear'])),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('show_reports', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('monday', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('tuesday', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('wednesday', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('thursday', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('friday', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('saturday', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sunday', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('school_days', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('schedule', ['MarkingPeriod'])

        # Adding model 'DaysOff'
        db.create_table('schedule_daysoff', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('marking_period', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.MarkingPeriod'])),
        ))
        db.send_create_signal('schedule', ['DaysOff'])

        # Adding model 'Period'
        db.create_table('schedule_period', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('start_time', self.gf('django.db.models.fields.TimeField')()),
            ('end_time', self.gf('django.db.models.fields.TimeField')()),
        ))
        db.send_create_signal('schedule', ['Period'])

        # Adding model 'CourseMeet'
        db.create_table('schedule_coursemeet', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('period', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.Period'])),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.Course'])),
            ('day', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.Location'], null=True, blank=True)),
        ))
        db.send_create_signal('schedule', ['CourseMeet'])

        # Adding model 'Location'
        db.create_table('schedule_location', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('schedule', ['Location'])

        # Adding model 'CourseEnrollment'
        db.create_table('schedule_courseenrollment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.Course'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.MdlUser'])),
            ('role', self.gf('django.db.models.fields.CharField')(default='Student', max_length=255, blank=True)),
            ('attendance_note', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('year', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.GradeLevel'], null=True, blank=True)),
        ))
        db.send_create_signal('schedule', ['CourseEnrollment'])

        # Adding unique constraint on 'CourseEnrollment', fields ['course', 'user', 'role']
        db.create_unique('schedule_courseenrollment', ['course_id', 'user_id', 'role'])

        # Adding M2M table for field exclude_days on 'CourseEnrollment'
        db.create_table('schedule_courseenrollment_exclude_days', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('courseenrollment', models.ForeignKey(orm['schedule.courseenrollment'], null=False)),
            ('day', models.ForeignKey(orm['schedule.day'], null=False))
        ))
        db.create_unique('schedule_courseenrollment_exclude_days', ['courseenrollment_id', 'day_id'])

        # Adding model 'Day'
        db.create_table('schedule_day', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('day', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('schedule', ['Day'])

        # Adding model 'Department'
        db.create_table('schedule_department', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('order_rank', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('schedule', ['Department'])

        # Adding model 'Course'
        db.create_table('schedule_course', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('fullname', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('shortname', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('teacher', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='ateacher', null=True, to=orm['sis.Faculty'])),
            ('homeroom', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('graded', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('credits', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=2, blank=True)),
            ('department', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.Department'], null=True, blank=True)),
            ('level', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.GradeLevel'], null=True, blank=True)),
            ('last_grade_submission', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('schedule', ['Course'])

        # Adding M2M table for field marking_period on 'Course'
        db.create_table('schedule_course_marking_period', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('course', models.ForeignKey(orm['schedule.course'], null=False)),
            ('markingperiod', models.ForeignKey(orm['schedule.markingperiod'], null=False))
        ))
        db.create_unique('schedule_course_marking_period', ['course_id', 'markingperiod_id'])

        # Adding M2M table for field secondary_teachers on 'Course'
        db.create_table('schedule_course_secondary_teachers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('course', models.ForeignKey(orm['schedule.course'], null=False)),
            ('faculty', models.ForeignKey(orm['sis.faculty'], null=False))
        ))
        db.create_unique('schedule_course_secondary_teachers', ['course_id', 'faculty_id'])

        # Adding model 'OmitCourseGPA'
        db.create_table('schedule_omitcoursegpa', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.Student'])),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.Course'])),
        ))
        db.send_create_signal('schedule', ['OmitCourseGPA'])

        # Adding model 'OmitYearGPA'
        db.create_table('schedule_omityeargpa', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.Student'])),
            ('year', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.SchoolYear'])),
        ))
        db.send_create_signal('schedule', ['OmitYearGPA'])

        # Adding model 'StandardTest'
        db.create_table('schedule_standardtest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('calculate_total', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('cherry_pick_categories', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('cherry_pick_final', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('show_on_reports', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('schedule', ['StandardTest'])

        # Adding model 'StandardCategory'
        db.create_table('schedule_standardcategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('test', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.StandardTest'])),
            ('is_total', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('schedule', ['StandardCategory'])

        # Adding model 'StandardTestResult'
        db.create_table('schedule_standardtestresult', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2012, 7, 19, 0, 0))),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.Student'])),
            ('test', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.StandardTest'])),
            ('show_on_reports', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('schedule', ['StandardTestResult'])

        # Adding unique constraint on 'StandardTestResult', fields ['date', 'student', 'test']
        db.create_unique('schedule_standardtestresult', ['date', 'student_id', 'test_id'])

        # Adding model 'StandardCategoryGrade'
        db.create_table('schedule_standardcategorygrade', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.StandardCategory'])),
            ('result', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.StandardTestResult'])),
            ('grade', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=2)),
        ))
        db.send_create_signal('schedule', ['StandardCategoryGrade'])

        # Adding model 'Award'
        db.create_table('schedule_award', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('schedule', ['Award'])

        # Adding model 'AwardStudent'
        db.create_table('schedule_awardstudent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('award', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.Award'])),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.Student'])),
            ('marking_period', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.MarkingPeriod'], null=True, blank=True)),
        ))
        db.send_create_signal('schedule', ['AwardStudent'])


    def backwards(self, orm):
        # Removing unique constraint on 'StandardTestResult', fields ['date', 'student', 'test']
        db.delete_unique('schedule_standardtestresult', ['date', 'student_id', 'test_id'])

        # Removing unique constraint on 'CourseEnrollment', fields ['course', 'user', 'role']
        db.delete_unique('schedule_courseenrollment', ['course_id', 'user_id', 'role'])

        # Deleting model 'MarkingPeriod'
        db.delete_table('schedule_markingperiod')

        # Deleting model 'DaysOff'
        db.delete_table('schedule_daysoff')

        # Deleting model 'Period'
        db.delete_table('schedule_period')

        # Deleting model 'CourseMeet'
        db.delete_table('schedule_coursemeet')

        # Deleting model 'Location'
        db.delete_table('schedule_location')

        # Deleting model 'CourseEnrollment'
        db.delete_table('schedule_courseenrollment')

        # Removing M2M table for field exclude_days on 'CourseEnrollment'
        db.delete_table('schedule_courseenrollment_exclude_days')

        # Deleting model 'Day'
        db.delete_table('schedule_day')

        # Deleting model 'Department'
        db.delete_table('schedule_department')

        # Deleting model 'Course'
        db.delete_table('schedule_course')

        # Removing M2M table for field marking_period on 'Course'
        db.delete_table('schedule_course_marking_period')

        # Removing M2M table for field secondary_teachers on 'Course'
        db.delete_table('schedule_course_secondary_teachers')

        # Deleting model 'OmitCourseGPA'
        db.delete_table('schedule_omitcoursegpa')

        # Deleting model 'OmitYearGPA'
        db.delete_table('schedule_omityeargpa')

        # Deleting model 'StandardTest'
        db.delete_table('schedule_standardtest')

        # Deleting model 'StandardCategory'
        db.delete_table('schedule_standardcategory')

        # Deleting model 'StandardTestResult'
        db.delete_table('schedule_standardtestresult')

        # Deleting model 'StandardCategoryGrade'
        db.delete_table('schedule_standardcategorygrade')

        # Deleting model 'Award'
        db.delete_table('schedule_award')

        # Deleting model 'AwardStudent'
        db.delete_table('schedule_awardstudent')


    models = {
        'schedule.award': {
            'Meta': {'object_name': 'Award'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'schedule.awardstudent': {
            'Meta': {'object_name': 'AwardStudent'},
            'award': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Award']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marking_period': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.MarkingPeriod']", 'null': 'True', 'blank': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.Student']"})
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
        'schedule.daysoff': {
            'Meta': {'object_name': 'DaysOff'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marking_period': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.MarkingPeriod']"})
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
        'schedule.omitcoursegpa': {
            'Meta': {'object_name': 'OmitCourseGPA'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.Student']"})
        },
        'schedule.omityeargpa': {
            'Meta': {'object_name': 'OmitYearGPA'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.Student']"}),
            'year': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.SchoolYear']"})
        },
        'schedule.period': {
            'Meta': {'ordering': "('start_time',)", 'object_name': 'Period'},
            'end_time': ('django.db.models.fields.TimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'start_time': ('django.db.models.fields.TimeField', [], {})
        },
        'schedule.standardcategory': {
            'Meta': {'object_name': 'StandardCategory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_total': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'test': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.StandardTest']"})
        },
        'schedule.standardcategorygrade': {
            'Meta': {'object_name': 'StandardCategoryGrade'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.StandardCategory']"}),
            'grade': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'result': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.StandardTestResult']"})
        },
        'schedule.standardtest': {
            'Meta': {'object_name': 'StandardTest'},
            'calculate_total': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'cherry_pick_categories': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'cherry_pick_final': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'show_on_reports': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'schedule.standardtestresult': {
            'Meta': {'unique_together': "(('date', 'student', 'test'),)", 'object_name': 'StandardTestResult'},
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 7, 19, 0, 0)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'show_on_reports': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.Student']"}),
            'test': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.StandardTest']"})
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
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
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
            'benchmark_grade': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'cohorts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sis.Cohort']", 'symmetrical': 'False', 'through': "orm['sis.StudentCohort']", 'blank': 'True'}),
            'date_dismissed': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'emergency_contacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sis.EmergencyContact']", 'symmetrical': 'False', 'blank': 'True'}),
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
            'year': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.GradeLevel']", 'null': 'True', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        'sis.studentcohort': {
            'Meta': {'object_name': 'StudentCohort', 'managed': 'False'},
            'cohort': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.Cohort']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.Student']"})
        }
    }

    complete_apps = ['schedule']