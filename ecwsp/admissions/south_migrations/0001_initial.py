# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AdmissionLevel'
        db.create_table(u'admissions_admissionlevel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('order', self.gf('django.db.models.fields.IntegerField')(unique=True)),
        ))
        db.send_create_signal(u'admissions', ['AdmissionLevel'])

        # Adding model 'AdmissionCheck'
        db.create_table(u'admissions_admissioncheck', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('level', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.AdmissionLevel'])),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'admissions', ['AdmissionCheck'])

        # Adding model 'EthnicityChoice'
        db.create_table(u'admissions_ethnicitychoice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'admissions', ['EthnicityChoice'])

        # Adding model 'ReligionChoice'
        db.create_table(u'admissions_religionchoice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'admissions', ['ReligionChoice'])

        # Adding model 'HeardAboutUsOption'
        db.create_table(u'admissions_heardaboutusoption', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'admissions', ['HeardAboutUsOption'])

        # Adding model 'FirstContactOption'
        db.create_table(u'admissions_firstcontactoption', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'admissions', ['FirstContactOption'])

        # Adding model 'ApplicationDecisionOption'
        db.create_table(u'admissions_applicationdecisionoption', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'admissions', ['ApplicationDecisionOption'])

        # Adding M2M table for field level on 'ApplicationDecisionOption'
        m2m_table_name = db.shorten_name(u'admissions_applicationdecisionoption_level')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('applicationdecisionoption', models.ForeignKey(orm[u'admissions.applicationdecisionoption'], null=False)),
            ('admissionlevel', models.ForeignKey(orm[u'admissions.admissionlevel'], null=False))
        ))
        db.create_unique(m2m_table_name, ['applicationdecisionoption_id', 'admissionlevel_id'])

        # Adding model 'BoroughOption'
        db.create_table(u'admissions_boroughoption', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'admissions', ['BoroughOption'])

        # Adding model 'SchoolType'
        db.create_table(u'admissions_schooltype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'admissions', ['SchoolType'])

        # Adding model 'PlaceOfWorship'
        db.create_table(u'admissions_placeofworship', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'admissions', ['PlaceOfWorship'])

        # Adding model 'FeederSchool'
        db.create_table(u'admissions_feederschool', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('school_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.SchoolType'], null=True, blank=True)),
        ))
        db.send_create_signal(u'admissions', ['FeederSchool'])

        # Adding model 'OpenHouse'
        db.create_table(u'admissions_openhouse', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'admissions', ['OpenHouse'])

        # Adding model 'WithdrawnChoices'
        db.create_table(u'admissions_withdrawnchoices', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal(u'admissions', ['WithdrawnChoices'])

        # Adding model 'CountryOption'
        db.create_table(u'admissions_countryoption', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal(u'admissions', ['CountryOption'])

        # Adding model 'ImmigrationOption'
        db.create_table(u'admissions_immigrationoption', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal(u'admissions', ['ImmigrationOption'])

        # Adding model 'Applicant'
        db.create_table(u'admissions_applicant', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('fname', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('mname', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('lname', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('pic', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('sex', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('bday', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('unique_id', self.gf('django.db.models.fields.IntegerField')(unique=True, null=True, blank=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=360, blank=True)),
            ('state', self.gf('localflavor.us.models.USStateField')(max_length=2, blank=True)),
            ('zip', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('ssn', self.gf('django.db.models.fields.CharField')(max_length=11, blank=True)),
            ('parent_email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('family_preferred_language', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['sis.LanguageChoice'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('year', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['sis.GradeLevel'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('school_year', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['sis.SchoolYear'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('ethnicity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.EthnicityChoice'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('hs_grad_yr', self.gf('django.db.models.fields.IntegerField')(max_length=4, null=True, blank=True)),
            ('elem_grad_yr', self.gf('django.db.models.fields.IntegerField')(max_length=4, null=True, blank=True)),
            ('present_school', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.FeederSchool'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('present_school_typed', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('present_school_type_typed', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('religion', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.ReligionChoice'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('place_of_worship', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.PlaceOfWorship'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('follow_up_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('parent_guardian_first_name', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('parent_guardian_last_name', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('relationship_to_student', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('heard_about_us', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.HeardAboutUsOption'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('from_online_inquiry', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('first_contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.FirstContactOption'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('borough', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.BoroughOption'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('country_of_birth', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.CountryOption'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('immigration_status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.ImmigrationOption'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('ready_for_export', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sis_student', self.gf('django.db.models.fields.related.OneToOneField')(related_name='appl_student', null=True, on_delete=models.SET_NULL, to=orm['sis.Student'], blank=True, unique=True)),
            ('total_income', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('adjusted_available_income', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('calculated_payment', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('date_added', self.gf('django.db.models.fields.DateField')(auto_now_add=True, null=True, blank=True)),
            ('level', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.AdmissionLevel'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('application_decision', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.ApplicationDecisionOption'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('application_decision_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('withdrawn', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.WithdrawnChoices'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('withdrawn_note', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('first_to_college', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('individual_education_plan', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('lives_with', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
        ))
        db.send_create_signal(u'admissions', ['Applicant'])

        # Adding M2M table for field siblings on 'Applicant'
        m2m_table_name = db.shorten_name(u'admissions_applicant_siblings')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('applicant', models.ForeignKey(orm[u'admissions.applicant'], null=False)),
            ('student', models.ForeignKey(orm[u'sis.student'], null=False))
        ))
        db.create_unique(m2m_table_name, ['applicant_id', 'student_id'])

        # Adding M2M table for field parent_guardians on 'Applicant'
        m2m_table_name = db.shorten_name(u'admissions_applicant_parent_guardians')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('applicant', models.ForeignKey(orm[u'admissions.applicant'], null=False)),
            ('emergencycontact', models.ForeignKey(orm[u'sis.emergencycontact'], null=False))
        ))
        db.create_unique(m2m_table_name, ['applicant_id', 'emergencycontact_id'])

        # Adding M2M table for field open_house_attended on 'Applicant'
        m2m_table_name = db.shorten_name(u'admissions_applicant_open_house_attended')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('applicant', models.ForeignKey(orm[u'admissions.applicant'], null=False)),
            ('openhouse', models.ForeignKey(orm[u'admissions.openhouse'], null=False))
        ))
        db.create_unique(m2m_table_name, ['applicant_id', 'openhouse_id'])

        # Adding M2M table for field checklist on 'Applicant'
        m2m_table_name = db.shorten_name(u'admissions_applicant_checklist')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('applicant', models.ForeignKey(orm[u'admissions.applicant'], null=False)),
            ('admissioncheck', models.ForeignKey(orm[u'admissions.admissioncheck'], null=False))
        ))
        db.create_unique(m2m_table_name, ['applicant_id', 'admissioncheck_id'])

        # Adding model 'ApplicantFile'
        db.create_table(u'admissions_applicantfile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('applicant_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('applicant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.Applicant'])),
        ))
        db.send_create_signal(u'admissions', ['ApplicantFile'])

        # Adding model 'ContactLog'
        db.create_table(u'admissions_contactlog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('applicant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.Applicant'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'admissions', ['ContactLog'])

        # Adding model 'ApplicantStandardTestResult'
        db.create_table(u'admissions_applicantstandardtestresult', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2013, 12, 27, 0, 0))),
            ('applicant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.Applicant'])),
            ('test', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['standard_test.StandardTest'])),
            ('show_on_reports', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'admissions', ['ApplicantStandardTestResult'])

        # Adding unique constraint on 'ApplicantStandardTestResult', fields ['date', 'applicant', 'test']
        db.create_unique(u'admissions_applicantstandardtestresult', ['date', 'applicant_id', 'test_id'])

        # Adding model 'ApplicantStandardCategoryGrade'
        db.create_table(u'admissions_applicantstandardcategorygrade', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['standard_test.StandardCategory'])),
            ('result', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['admissions.ApplicantStandardTestResult'])),
            ('grade', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=2)),
        ))
        db.send_create_signal(u'admissions', ['ApplicantStandardCategoryGrade'])


    def backwards(self, orm):
        # Removing unique constraint on 'ApplicantStandardTestResult', fields ['date', 'applicant', 'test']
        db.delete_unique(u'admissions_applicantstandardtestresult', ['date', 'applicant_id', 'test_id'])

        # Deleting model 'AdmissionLevel'
        db.delete_table(u'admissions_admissionlevel')

        # Deleting model 'AdmissionCheck'
        db.delete_table(u'admissions_admissioncheck')

        # Deleting model 'EthnicityChoice'
        db.delete_table(u'admissions_ethnicitychoice')

        # Deleting model 'ReligionChoice'
        db.delete_table(u'admissions_religionchoice')

        # Deleting model 'HeardAboutUsOption'
        db.delete_table(u'admissions_heardaboutusoption')

        # Deleting model 'FirstContactOption'
        db.delete_table(u'admissions_firstcontactoption')

        # Deleting model 'ApplicationDecisionOption'
        db.delete_table(u'admissions_applicationdecisionoption')

        # Removing M2M table for field level on 'ApplicationDecisionOption'
        db.delete_table(db.shorten_name(u'admissions_applicationdecisionoption_level'))

        # Deleting model 'BoroughOption'
        db.delete_table(u'admissions_boroughoption')

        # Deleting model 'SchoolType'
        db.delete_table(u'admissions_schooltype')

        # Deleting model 'PlaceOfWorship'
        db.delete_table(u'admissions_placeofworship')

        # Deleting model 'FeederSchool'
        db.delete_table(u'admissions_feederschool')

        # Deleting model 'OpenHouse'
        db.delete_table(u'admissions_openhouse')

        # Deleting model 'WithdrawnChoices'
        db.delete_table(u'admissions_withdrawnchoices')

        # Deleting model 'CountryOption'
        db.delete_table(u'admissions_countryoption')

        # Deleting model 'ImmigrationOption'
        db.delete_table(u'admissions_immigrationoption')

        # Deleting model 'Applicant'
        db.delete_table(u'admissions_applicant')

        # Removing M2M table for field siblings on 'Applicant'
        db.delete_table(db.shorten_name(u'admissions_applicant_siblings'))

        # Removing M2M table for field parent_guardians on 'Applicant'
        db.delete_table(db.shorten_name(u'admissions_applicant_parent_guardians'))

        # Removing M2M table for field open_house_attended on 'Applicant'
        db.delete_table(db.shorten_name(u'admissions_applicant_open_house_attended'))

        # Removing M2M table for field checklist on 'Applicant'
        db.delete_table(db.shorten_name(u'admissions_applicant_checklist'))

        # Deleting model 'ApplicantFile'
        db.delete_table(u'admissions_applicantfile')

        # Deleting model 'ContactLog'
        db.delete_table(u'admissions_contactlog')

        # Deleting model 'ApplicantStandardTestResult'
        db.delete_table(u'admissions_applicantstandardtestresult')

        # Deleting model 'ApplicantStandardCategoryGrade'
        db.delete_table(u'admissions_applicantstandardcategorygrade')


    models = {
        u'admissions.admissioncheck': {
            'Meta': {'ordering': "('level', 'name')", 'object_name': 'AdmissionCheck'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admissions.AdmissionLevel']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'admissions.admissionlevel': {
            'Meta': {'ordering': "('order',)", 'object_name': 'AdmissionLevel'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        },
        u'admissions.applicant': {
            'Meta': {'ordering': "('lname', 'fname')", 'object_name': 'Applicant'},
            'adjusted_available_income': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'application_decision': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admissions.ApplicationDecisionOption']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'application_decision_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'bday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'borough': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admissions.BoroughOption']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'calculated_payment': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'checklist': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['admissions.AdmissionCheck']", 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '360', 'blank': 'True'}),
            'country_of_birth': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admissions.CountryOption']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'elem_grad_yr': ('django.db.models.fields.IntegerField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'ethnicity': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admissions.EthnicityChoice']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'family_preferred_language': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['sis.LanguageChoice']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'first_contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admissions.FirstContactOption']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'first_to_college': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'fname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'follow_up_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'from_online_inquiry': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'heard_about_us': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admissions.HeardAboutUsOption']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'hs_grad_yr': ('django.db.models.fields.IntegerField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'immigration_status': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admissions.ImmigrationOption']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'individual_education_plan': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admissions.AdmissionLevel']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'lives_with': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'lname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'mname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'open_house_attended': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['admissions.OpenHouse']", 'null': 'True', 'blank': 'True'}),
            'parent_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'parent_guardian_first_name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'parent_guardian_last_name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'parent_guardians': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['sis.EmergencyContact']", 'null': 'True', 'blank': 'True'}),
            'pic': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'place_of_worship': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admissions.PlaceOfWorship']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'present_school': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admissions.FeederSchool']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'present_school_type_typed': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'present_school_typed': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'ready_for_export': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'relationship_to_student': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'religion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admissions.ReligionChoice']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'school_year': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['sis.SchoolYear']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'siblings': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'+'", 'blank': 'True', 'to': u"orm['sis.Student']"}),
            'sis_student': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'appl_student'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['sis.Student']", 'blank': 'True', 'unique': 'True'}),
            'ssn': ('django.db.models.fields.CharField', [], {'max_length': '11', 'blank': 'True'}),
            'state': ('localflavor.us.models.USStateField', [], {'max_length': '2', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'total_income': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'unique_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'withdrawn': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admissions.WithdrawnChoices']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'withdrawn_note': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'year': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['sis.GradeLevel']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        u'admissions.applicantfile': {
            'Meta': {'object_name': 'ApplicantFile'},
            'applicant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admissions.Applicant']"}),
            'applicant_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'admissions.applicantstandardcategorygrade': {
            'Meta': {'object_name': 'ApplicantStandardCategoryGrade'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['standard_test.StandardCategory']"}),
            'grade': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'result': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admissions.ApplicantStandardTestResult']"})
        },
        u'admissions.applicantstandardtestresult': {
            'Meta': {'unique_together': "(('date', 'applicant', 'test'),)", 'object_name': 'ApplicantStandardTestResult'},
            'applicant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admissions.Applicant']"}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 12, 27, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'show_on_reports': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'test': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['standard_test.StandardTest']"})
        },
        u'admissions.applicationdecisionoption': {
            'Meta': {'object_name': 'ApplicationDecisionOption'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['admissions.AdmissionLevel']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'admissions.boroughoption': {
            'Meta': {'ordering': "['name']", 'object_name': 'BoroughOption'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'admissions.contactlog': {
            'Meta': {'object_name': 'ContactLog'},
            'applicant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admissions.Applicant']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'admissions.countryoption': {
            'Meta': {'ordering': "['name']", 'object_name': 'CountryOption'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'admissions.ethnicitychoice': {
            'Meta': {'ordering': "['name']", 'object_name': 'EthnicityChoice'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'admissions.feederschool': {
            'Meta': {'ordering': "['name']", 'object_name': 'FeederSchool'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'school_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['admissions.SchoolType']", 'null': 'True', 'blank': 'True'})
        },
        u'admissions.firstcontactoption': {
            'Meta': {'ordering': "['name']", 'object_name': 'FirstContactOption'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'admissions.heardaboutusoption': {
            'Meta': {'ordering': "['name']", 'object_name': 'HeardAboutUsOption'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'admissions.immigrationoption': {
            'Meta': {'ordering': "['name']", 'object_name': 'ImmigrationOption'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'admissions.openhouse': {
            'Meta': {'ordering': "('-date',)", 'object_name': 'OpenHouse'},
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'admissions.placeofworship': {
            'Meta': {'object_name': 'PlaceOfWorship'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'admissions.religionchoice': {
            'Meta': {'ordering': "['name']", 'object_name': 'ReligionChoice'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'admissions.schooltype': {
            'Meta': {'object_name': 'SchoolType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'admissions.withdrawnchoices': {
            'Meta': {'ordering': "['name']", 'object_name': 'WithdrawnChoices'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
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
            'students': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'student_cohorts'", 'blank': 'True', 'to': u"orm['sis.Student']"})
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
            'benchmark_grade': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'cache_gpa': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'class_of_year': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.ClassYear']", 'null': 'True', 'blank': 'True'}),
            'cohorts': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sis.Cohort']", 'symmetrical': 'False', 'blank': 'True'}),
            'date_dismissed': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'emergency_contacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sis.EmergencyContact']", 'symmetrical': 'False', 'blank': 'True'}),
            'family_access_users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'+'", 'blank': 'True', 'to': u"orm['auth.User']"}),
            'family_preferred_language': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['sis.LanguageChoice']", 'null': 'True', 'blank': 'True'}),
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
        },
        u'standard_test.standardcategory': {
            'Meta': {'object_name': 'StandardCategory'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_total': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'test': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['standard_test.StandardTest']"})
        },
        u'standard_test.standardtest': {
            'Meta': {'object_name': 'StandardTest'},
            'calculate_total': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'cherry_pick_categories': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'cherry_pick_final': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'show_on_reports': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        }
    }

    complete_apps = ['admissions']