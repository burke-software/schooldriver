# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Hours'
        db.create_table('volunteer_track_hours', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('volunteer_site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['volunteer_track.VolunteerSite'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('hours', self.gf('django.db.models.fields.FloatField')()),
            ('time_stamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('volunteer_track', ['Hours'])

        # Adding unique constraint on 'Hours', fields ['volunteer_site', 'date']
        db.create_unique('volunteer_track_hours', ['volunteer_site_id', 'date'])

        # Adding model 'Site'
        db.create_table('volunteer_track_site', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('site_address', self.gf('django.db.models.fields.CharField')(max_length=511)),
            ('site_city', self.gf('django.db.models.fields.CharField')(max_length=768)),
            ('site_state', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('site_zip', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('volunteer_track', ['Site'])

        # Adding model 'SiteSupervisor'
        db.create_table('volunteer_track_sitesupervisor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['volunteer_track.Site'], null=True, blank=True)),
            ('phone', self.gf('django.contrib.localflavor.us.models.PhoneNumberField')(max_length=20, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=200, blank=True)),
        ))
        db.send_create_signal('volunteer_track', ['SiteSupervisor'])

        # Adding model 'VolunteerSite'
        db.create_table('volunteer_track_volunteersite', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('inactive', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('volunteer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['volunteer_track.Volunteer'])),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['volunteer_track.Site'])),
            ('supervisor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['volunteer_track.SiteSupervisor'], null=True, blank=True)),
            ('site_approval', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('contract', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('job_description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('hours_confirmed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('secret_key', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
        ))
        db.send_create_signal('volunteer_track', ['VolunteerSite'])

        # Adding model 'Volunteer'
        db.create_table('volunteer_track_volunteer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('student', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['sis.Student'], unique=True)),
            ('attended_reflection', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('hours_required', self.gf('django.db.models.fields.IntegerField')(default=u'20', null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('email_queue', self.gf('django.db.models.fields.CharField')(default='', max_length=1000, blank=True)),
        ))
        db.send_create_signal('volunteer_track', ['Volunteer'])


    def backwards(self, orm):
        # Removing unique constraint on 'Hours', fields ['volunteer_site', 'date']
        db.delete_unique('volunteer_track_hours', ['volunteer_site_id', 'date'])

        # Deleting model 'Hours'
        db.delete_table('volunteer_track_hours')

        # Deleting model 'Site'
        db.delete_table('volunteer_track_site')

        # Deleting model 'SiteSupervisor'
        db.delete_table('volunteer_track_sitesupervisor')

        # Deleting model 'VolunteerSite'
        db.delete_table('volunteer_track_volunteersite')

        # Deleting model 'Volunteer'
        db.delete_table('volunteer_track_volunteer')


    models = {
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
        },
        'volunteer_track.hours': {
            'Meta': {'unique_together': "(('volunteer_site', 'date'),)", 'object_name': 'Hours'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'hours': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'time_stamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'volunteer_site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['volunteer_track.VolunteerSite']"})
        },
        'volunteer_track.site': {
            'Meta': {'object_name': 'Site'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site_address': ('django.db.models.fields.CharField', [], {'max_length': '511'}),
            'site_city': ('django.db.models.fields.CharField', [], {'max_length': '768'}),
            'site_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'site_state': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'site_zip': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'volunteer_track.sitesupervisor': {
            'Meta': {'object_name': 'SiteSupervisor'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['volunteer_track.Site']", 'null': 'True', 'blank': 'True'})
        },
        'volunteer_track.volunteer': {
            'Meta': {'object_name': 'Volunteer'},
            'attended_reflection': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email_queue': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000', 'blank': 'True'}),
            'hours_required': ('django.db.models.fields.IntegerField', [], {'default': "u'20'", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['volunteer_track.Site']", 'null': 'True', 'through': "orm['volunteer_track.VolunteerSite']", 'blank': 'True'}),
            'student': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sis.Student']", 'unique': 'True'})
        },
        'volunteer_track.volunteersite': {
            'Meta': {'object_name': 'VolunteerSite'},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'contract': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hours_confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inactive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'job_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'secret_key': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['volunteer_track.Site']"}),
            'site_approval': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'supervisor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['volunteer_track.SiteSupervisor']", 'null': 'True', 'blank': 'True'}),
            'volunteer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['volunteer_track.Volunteer']"})
        }
    }

    complete_apps = ['volunteer_track']