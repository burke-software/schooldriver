# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Scale'
        db.create_table('benchmark_grade_scale', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=127)),
            ('minimum', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
            ('maximum', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
            ('decimalPlaces', self.gf('django.db.models.fields.IntegerField')(default=2)),
            ('symbol', self.gf('django.db.models.fields.CharField')(max_length=7, blank=True)),
        ))
        db.send_create_signal('benchmark_grade', ['Scale'])

        # Adding model 'Mapping'
        db.create_table('benchmark_grade_mapping', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=127)),
            ('scale', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['benchmark_grade.Scale'])),
            ('minOperator', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('minimum', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
            ('maxOperator', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('maximum', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
        ))
        db.send_create_signal('benchmark_grade', ['Mapping'])

        # Adding unique constraint on 'Mapping', fields ['name', 'scale']
        db.create_unique('benchmark_grade_mapping', ['name', 'scale_id'])

        # Adding model 'Category'
        db.create_table('benchmark_grade_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('weight', self.gf('django.db.models.fields.DecimalField')(default=1, max_digits=8, decimal_places=2)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.Course'], null=True, blank=True)),
        ))
        db.send_create_signal('benchmark_grade', ['Category'])

        # Adding model 'Item'
        db.create_table('benchmark_grade_item', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.Course'])),
            ('date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('markingPeriod', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.MarkingPeriod'], null=True, blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['benchmark_grade.Category'])),
            ('scale', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['benchmark_grade.Scale'])),
            ('multiplier', self.gf('django.db.models.fields.DecimalField')(default=1, max_digits=8, decimal_places=2)),
        ))
        db.send_create_signal('benchmark_grade', ['Item'])

        # Adding model 'Mark'
        db.create_table('benchmark_grade_mark', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['benchmark_grade.Item'])),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.Student'])),
            ('mark', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=2, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('excused', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('benchmark_grade', ['Mark'])

        # Adding model 'Aggregate'
        db.create_table('benchmark_grade_aggregate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('scale', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['benchmark_grade.Scale'])),
            ('manualMark', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=2, blank=True)),
            ('cachedValue', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=2, blank=True)),
            ('singleStudent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='single_student', null=True, to=orm['sis.Student'])),
            ('singleCourse', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='single_course', null=True, to=orm['schedule.Course'])),
            ('singleCategory', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='single_category', null=True, to=orm['benchmark_grade.Category'])),
            ('singleMarkingPeriod', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schedule.MarkingPeriod'], null=True, blank=True)),
        ))
        db.send_create_signal('benchmark_grade', ['Aggregate'])

        # Adding M2M table for field student on 'Aggregate'
        db.create_table('benchmark_grade_aggregate_student', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('aggregate', models.ForeignKey(orm['benchmark_grade.aggregate'], null=False)),
            ('student', models.ForeignKey(orm['sis.student'], null=False))
        ))
        db.create_unique('benchmark_grade_aggregate_student', ['aggregate_id', 'student_id'])

        # Adding M2M table for field course on 'Aggregate'
        db.create_table('benchmark_grade_aggregate_course', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('aggregate', models.ForeignKey(orm['benchmark_grade.aggregate'], null=False)),
            ('course', models.ForeignKey(orm['schedule.course'], null=False))
        ))
        db.create_unique('benchmark_grade_aggregate_course', ['aggregate_id', 'course_id'])

        # Adding M2M table for field category on 'Aggregate'
        db.create_table('benchmark_grade_aggregate_category', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('aggregate', models.ForeignKey(orm['benchmark_grade.aggregate'], null=False)),
            ('category', models.ForeignKey(orm['benchmark_grade.category'], null=False))
        ))
        db.create_unique('benchmark_grade_aggregate_category', ['aggregate_id', 'category_id'])

        # Adding M2M table for field aggregate on 'Aggregate'
        db.create_table('benchmark_grade_aggregate_aggregate', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_aggregate', models.ForeignKey(orm['benchmark_grade.aggregate'], null=False)),
            ('to_aggregate', models.ForeignKey(orm['benchmark_grade.aggregate'], null=False))
        ))
        db.create_unique('benchmark_grade_aggregate_aggregate', ['from_aggregate_id', 'to_aggregate_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Mapping', fields ['name', 'scale']
        db.delete_unique('benchmark_grade_mapping', ['name', 'scale_id'])

        # Deleting model 'Scale'
        db.delete_table('benchmark_grade_scale')

        # Deleting model 'Mapping'
        db.delete_table('benchmark_grade_mapping')

        # Deleting model 'Category'
        db.delete_table('benchmark_grade_category')

        # Deleting model 'Item'
        db.delete_table('benchmark_grade_item')

        # Deleting model 'Mark'
        db.delete_table('benchmark_grade_mark')

        # Deleting model 'Aggregate'
        db.delete_table('benchmark_grade_aggregate')

        # Removing M2M table for field student on 'Aggregate'
        db.delete_table('benchmark_grade_aggregate_student')

        # Removing M2M table for field course on 'Aggregate'
        db.delete_table('benchmark_grade_aggregate_course')

        # Removing M2M table for field category on 'Aggregate'
        db.delete_table('benchmark_grade_aggregate_category')

        # Removing M2M table for field aggregate on 'Aggregate'
        db.delete_table('benchmark_grade_aggregate_aggregate')


    models = {
        'benchmark_grade.aggregate': {
            'Meta': {'object_name': 'Aggregate'},
            'aggregate': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'aggregate_rel_+'", 'null': 'True', 'to': "orm['benchmark_grade.Aggregate']"}),
            'cachedValue': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['benchmark_grade.Category']", 'null': 'True', 'blank': 'True'}),
            'course': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['schedule.Course']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manualMark': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'scale': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['benchmark_grade.Scale']"}),
            'singleCategory': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'single_category'", 'null': 'True', 'to': "orm['benchmark_grade.Category']"}),
            'singleCourse': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'single_course'", 'null': 'True', 'to': "orm['schedule.Course']"}),
            'singleMarkingPeriod': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.MarkingPeriod']", 'null': 'True', 'blank': 'True'}),
            'singleStudent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'single_student'", 'null': 'True', 'to': "orm['sis.Student']"}),
            'student': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sis.Student']", 'null': 'True', 'blank': 'True'})
        },
        'benchmark_grade.category': {
            'Meta': {'object_name': 'Category'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Course']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'weight': ('django.db.models.fields.DecimalField', [], {'default': '1', 'max_digits': '8', 'decimal_places': '2'})
        },
        'benchmark_grade.item': {
            'Meta': {'object_name': 'Item'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['benchmark_grade.Category']"}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.Course']"}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'markingPeriod': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schedule.MarkingPeriod']", 'null': 'True', 'blank': 'True'}),
            'multiplier': ('django.db.models.fields.DecimalField', [], {'default': '1', 'max_digits': '8', 'decimal_places': '2'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'scale': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['benchmark_grade.Scale']"})
        },
        'benchmark_grade.mapping': {
            'Meta': {'unique_together': "(('name', 'scale'),)", 'object_name': 'Mapping'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maxOperator': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'maximum': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'minOperator': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'minimum': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '127'}),
            'scale': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['benchmark_grade.Scale']"})
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
        'benchmark_grade.scale': {
            'Meta': {'object_name': 'Scale'},
            'decimalPlaces': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maximum': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'minimum': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '127'}),
            'symbol': ('django.db.models.fields.CharField', [], {'max_length': '7', 'blank': 'True'})
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

    complete_apps = ['benchmark_grade']