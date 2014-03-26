# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CourseSync'
        db.create_table(u'engrade_sync_coursesync', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.Course'])),
            ('marking_period', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.MarkingPeriod'])),
            ('engrade_course_id', self.gf('django.db.models.fields.BigIntegerField')(unique=True)),
        ))
        db.send_create_signal(u'engrade_sync', ['CourseSync'])

        # Adding unique constraint on 'CourseSync', fields ['course', 'marking_period']
        db.create_unique(u'engrade_sync_coursesync', ['course_id', 'marking_period_id'])

        # Adding model 'TeacherSync'
        db.create_table(u'engrade_sync_teachersync', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('teacher', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.Faculty'], unique=True)),
            ('engrade_teacher_id', self.gf('django.db.models.fields.BigIntegerField')(unique=True)),
        ))
        db.send_create_signal(u'engrade_sync', ['TeacherSync'])


    def backwards(self, orm):
        # Removing unique constraint on 'CourseSync', fields ['course', 'marking_period']
        db.delete_unique(u'engrade_sync_coursesync', ['course_id', 'marking_period_id'])

        # Deleting model 'CourseSync'
        db.delete_table(u'engrade_sync_coursesync')

        # Deleting model 'TeacherSync'
        db.delete_table(u'engrade_sync_teachersync')


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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'engrade_sync.coursesync': {
            'Meta': {'unique_together': "(('course', 'marking_period'),)", 'object_name': 'CourseSync'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['schedule.Course']"}),
            'engrade_course_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marking_period': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['schedule.MarkingPeriod']"})
        },
        u'engrade_sync.teachersync': {
            'Meta': {'object_name': 'TeacherSync'},
            'engrade_teacher_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'teacher': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.Faculty']", 'unique': 'True'})
        },
        u'schedule.course': {
            'Meta': {'object_name': 'Course'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
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
        u'sis.schoolyear': {
            'Meta': {'ordering': "('-start_date',)", 'object_name': 'SchoolYear'},
            'active_year': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'benchmark_grade': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'grad_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        }
    }

    complete_apps = ['engrade_sync']