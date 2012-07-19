# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AdmissionLevel'
        db.create_table('admissions_admissionlevel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('order', self.gf('django.db.models.fields.IntegerField')(unique=True)),
        ))
        db.send_create_signal('admissions', ['AdmissionLevel'])

        # Adding model 'AdmissionCheck'
        db.create_table('admissions_admissioncheck', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('level', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.AdmissionLevel'])),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('admissions', ['AdmissionCheck'])

        # Adding model 'EthnicityChoice'
        db.create_table('admissions_ethnicitychoice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('admissions', ['EthnicityChoice'])

        # Adding model 'ReligionChoice'
        db.create_table('admissions_religionchoice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('admissions', ['ReligionChoice'])

        # Adding model 'HeardAboutUsOption'
        db.create_table('admissions_heardaboutusoption', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('admissions', ['HeardAboutUsOption'])

        # Adding model 'FirstContactOption'
        db.create_table('admissions_firstcontactoption', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('admissions', ['FirstContactOption'])

        # Adding model 'ApplicationDecisionOption'
        db.create_table('admissions_applicationdecisionoption', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('admissions', ['ApplicationDecisionOption'])

        # Adding M2M table for field level on 'ApplicationDecisionOption'
        db.create_table('admissions_applicationdecisionoption_level', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('applicationdecisionoption', models.ForeignKey(orm['admissions.applicationdecisionoption'], null=False)),
            ('admissionlevel', models.ForeignKey(orm['admissions.admissionlevel'], null=False))
        ))
        db.create_unique('admissions_applicationdecisionoption_level', ['applicationdecisionoption_id', 'admissionlevel_id'])

        # Adding model 'BoroughOption'
        db.create_table('admissions_boroughoption', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('admissions', ['BoroughOption'])

        # Adding model 'FeederSchool'
        db.create_table('admissions_feederschool', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('admissions', ['FeederSchool'])

        # Adding model 'OpenHouse'
        db.create_table('admissions_openhouse', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('admissions', ['OpenHouse'])

        # Adding model 'WithdrawnChoices'
        db.create_table('admissions_withdrawnchoices', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal('admissions', ['WithdrawnChoices'])

        # Adding model 'CountryOption'
        db.create_table('admissions_countryoption', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal('admissions', ['CountryOption'])

        # Adding model 'ImmigrationOption'
        db.create_table('admissions_immigrationoption', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal('admissions', ['ImmigrationOption'])

        # Adding model 'Applicant'
        db.create_table('admissions_applicant', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('fname', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('mname', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('lname', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('sex', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('bday', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('unique_id', self.gf('django.db.models.fields.IntegerField')(unique=True, null=True, blank=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=360, blank=True)),
            ('state', self.gf('django.contrib.localflavor.us.models.USStateField')(max_length=2, blank=True)),
            ('zip', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('ssn', self.gf('django.db.models.fields.CharField')(max_length=11, blank=True)),
            ('parent_email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('year', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.GradeLevel'], null=True, blank=True)),
            ('school_year', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.SchoolYear'], null=True, blank=True)),
            ('ethnicity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.EthnicityChoice'], null=True, blank=True)),
            ('hs_grad_yr', self.gf('django.db.models.fields.IntegerField')(max_length=4, null=True, blank=True)),
            ('elem_grad_yr', self.gf('django.db.models.fields.IntegerField')(max_length=4, null=True, blank=True)),
            ('present_school', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.FeederSchool'], null=True, blank=True)),
            ('religion', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.ReligionChoice'], null=True, blank=True)),
            ('parent_guardian_first_name', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('parent_guardian_last_name', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('relationship_to_student', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('heard_about_us', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.HeardAboutUsOption'], null=True, blank=True)),
            ('first_contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.FirstContactOption'], null=True, blank=True)),
            ('borough', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.BoroughOption'], null=True, blank=True)),
            ('country_of_birth', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.CountryOption'], null=True, blank=True)),
            ('immigration_status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.ImmigrationOption'], null=True, blank=True)),
            ('ready_for_export', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sis_student', self.gf('django.db.models.fields.related.OneToOneField')(related_name='appl_student', null=True, on_delete=models.SET_NULL, to=orm['sis.Student'], blank=True, unique=True)),
            ('total_income', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('adjusted_available_income', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('calculated_payment', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('date_added', self.gf('django.db.models.fields.DateField')(auto_now_add=True, null=True, blank=True)),
            ('level', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.AdmissionLevel'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('application_decision', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.ApplicationDecisionOption'], null=True, blank=True)),
            ('application_decision_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('withdrawn', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.WithdrawnChoices'], null=True, blank=True)),
            ('withdrawn_note', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
        ))
        db.send_create_signal('admissions', ['Applicant'])

        # Adding M2M table for field siblings on 'Applicant'
        db.create_table('admissions_applicant_siblings', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('applicant', models.ForeignKey(orm['admissions.applicant'], null=False)),
            ('student', models.ForeignKey(orm['sis.student'], null=False))
        ))
        db.create_unique('admissions_applicant_siblings', ['applicant_id', 'student_id'])

        # Adding M2M table for field parent_guardians on 'Applicant'
        db.create_table('admissions_applicant_parent_guardians', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('applicant', models.ForeignKey(orm['admissions.applicant'], null=False)),
            ('emergencycontact', models.ForeignKey(orm['sis.emergencycontact'], null=False))
        ))
        db.create_unique('admissions_applicant_parent_guardians', ['applicant_id', 'emergencycontact_id'])

        # Adding M2M table for field open_house_attended on 'Applicant'
        db.create_table('admissions_applicant_open_house_attended', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('applicant', models.ForeignKey(orm['admissions.applicant'], null=False)),
            ('openhouse', models.ForeignKey(orm['admissions.openhouse'], null=False))
        ))
        db.create_unique('admissions_applicant_open_house_attended', ['applicant_id', 'openhouse_id'])

        # Adding M2M table for field checklist on 'Applicant'
        db.create_table('admissions_applicant_checklist', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('applicant', models.ForeignKey(orm['admissions.applicant'], null=False)),
            ('admissioncheck', models.ForeignKey(orm['admissions.admissioncheck'], null=False))
        ))
        db.create_unique('admissions_applicant_checklist', ['applicant_id', 'admissioncheck_id'])

        # Adding model 'ContactLog'
        db.create_table('admissions_contactlog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('applicant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.Applicant'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('admissions', ['ContactLog'])


    def backwards(self, orm):
        # Deleting model 'AdmissionLevel'
        db.delete_table('admissions_admissionlevel')

        # Deleting model 'AdmissionCheck'
        db.delete_table('admissions_admissioncheck')

        # Deleting model 'EthnicityChoice'
        db.delete_table('admissions_ethnicitychoice')

        # Deleting model 'ReligionChoice'
        db.delete_table('admissions_religionchoice')

        # Deleting model 'HeardAboutUsOption'
        db.delete_table('admissions_heardaboutusoption')

        # Deleting model 'FirstContactOption'
        db.delete_table('admissions_firstcontactoption')

        # Deleting model 'ApplicationDecisionOption'
        db.delete_table('admissions_applicationdecisionoption')

        # Removing M2M table for field level on 'ApplicationDecisionOption'
        db.delete_table('admissions_applicationdecisionoption_level')

        # Deleting model 'BoroughOption'
        db.delete_table('admissions_boroughoption')

        # Deleting model 'FeederSchool'
        db.delete_table('admissions_feederschool')

        # Deleting model 'OpenHouse'
        db.delete_table('admissions_openhouse')

        # Deleting model 'WithdrawnChoices'
        db.delete_table('admissions_withdrawnchoices')

        # Deleting model 'CountryOption'
        db.delete_table('admissions_countryoption')

        # Deleting model 'ImmigrationOption'
        db.delete_table('admissions_immigrationoption')

        # Deleting model 'Applicant'
        db.delete_table('admissions_applicant')

        # Removing M2M table for field siblings on 'Applicant'
        db.delete_table('admissions_applicant_siblings')

        # Removing M2M table for field parent_guardians on 'Applicant'
        db.delete_table('admissions_applicant_parent_guardians')

        # Removing M2M table for field open_house_attended on 'Applicant'
        db.delete_table('admissions_applicant_open_house_attended')

        # Removing M2M table for field checklist on 'Applicant'
        db.delete_table('admissions_applicant_checklist')

        # Deleting model 'ContactLog'
        db.delete_table('admissions_contactlog')


    models = {
        'admissions.admissioncheck': {
            'Meta': {'ordering': "('level', 'name')", 'object_name': 'AdmissionCheck'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['admissions.AdmissionLevel']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'admissions.admissionlevel': {
            'Meta': {'ordering': "('order',)", 'object_name': 'AdmissionLevel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        },
        'admissions.applicant': {
            'Meta': {'ordering': "('lname', 'fname')", 'object_name': 'Applicant'},
            'adjusted_available_income': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'application_decision': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['admissions.ApplicationDecisionOption']", 'null': 'True', 'blank': 'True'}),
            'application_decision_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'bday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'borough': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['admissions.BoroughOption']", 'null': 'True', 'blank': 'True'}),
            'calculated_payment': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'checklist': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['admissions.AdmissionCheck']", 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '360', 'blank': 'True'}),
            'country_of_birth': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['admissions.CountryOption']", 'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'elem_grad_yr': ('django.db.models.fields.IntegerField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'ethnicity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['admissions.EthnicityChoice']", 'null': 'True', 'blank': 'True'}),
            'first_contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['admissions.FirstContactOption']", 'null': 'True', 'blank': 'True'}),
            'fname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'heard_about_us': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['admissions.HeardAboutUsOption']", 'null': 'True', 'blank': 'True'}),
            'hs_grad_yr': ('django.db.models.fields.IntegerField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'immigration_status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['admissions.ImmigrationOption']", 'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['admissions.AdmissionLevel']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'lname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'mname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'open_house_attended': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['admissions.OpenHouse']", 'null': 'True', 'blank': 'True'}),
            'parent_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'parent_guardian_first_name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'parent_guardian_last_name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'parent_guardians': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sis.EmergencyContact']", 'null': 'True', 'blank': 'True'}),
            'present_school': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['admissions.FeederSchool']", 'null': 'True', 'blank': 'True'}),
            'ready_for_export': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'relationship_to_student': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'religion': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['admissions.ReligionChoice']", 'null': 'True', 'blank': 'True'}),
            'school_year': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.SchoolYear']", 'null': 'True', 'blank': 'True'}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'siblings': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sis.Student']", 'symmetrical': 'False', 'blank': 'True'}),
            'sis_student': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'appl_student'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['sis.Student']", 'blank': 'True', 'unique': 'True'}),
            'ssn': ('django.db.models.fields.CharField', [], {'max_length': '11', 'blank': 'True'}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'total_income': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'unique_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'withdrawn': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['admissions.WithdrawnChoices']", 'null': 'True', 'blank': 'True'}),
            'withdrawn_note': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'year': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sis.GradeLevel']", 'null': 'True', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        'admissions.applicationdecisionoption': {
            'Meta': {'object_name': 'ApplicationDecisionOption'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['admissions.AdmissionLevel']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'admissions.boroughoption': {
            'Meta': {'ordering': "['name']", 'object_name': 'BoroughOption'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'admissions.contactlog': {
            'Meta': {'object_name': 'ContactLog'},
            'applicant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['admissions.Applicant']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'admissions.countryoption': {
            'Meta': {'ordering': "['name']", 'object_name': 'CountryOption'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'admissions.ethnicitychoice': {
            'Meta': {'ordering': "['name']", 'object_name': 'EthnicityChoice'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'admissions.feederschool': {
            'Meta': {'ordering': "['name']", 'object_name': 'FeederSchool'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'admissions.firstcontactoption': {
            'Meta': {'ordering': "['name']", 'object_name': 'FirstContactOption'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'admissions.heardaboutusoption': {
            'Meta': {'ordering': "['name']", 'object_name': 'HeardAboutUsOption'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'admissions.immigrationoption': {
            'Meta': {'ordering': "['name']", 'object_name': 'ImmigrationOption'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'admissions.openhouse': {
            'Meta': {'ordering': "('-date',)", 'object_name': 'OpenHouse'},
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'admissions.religionchoice': {
            'Meta': {'ordering': "['name']", 'object_name': 'ReligionChoice'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'admissions.withdrawnchoices': {
            'Meta': {'ordering': "['name']", 'object_name': 'WithdrawnChoices'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
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
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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

    complete_apps = ['admissions']