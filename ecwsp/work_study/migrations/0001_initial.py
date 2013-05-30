# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CraContact'
        db.create_table(u'work_study_cracontact', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('email', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('email_all', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'work_study', ['CraContact'])

        # Adding model 'PickupLocation'
        db.create_table(u'work_study_pickuplocation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('location', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20)),
            ('long_name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('directions', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'work_study', ['PickupLocation'])

        # Adding model 'Contact'
        db.create_table(u'work_study_contact', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('guid', self.gf('django.db.models.fields.CharField')(max_length=36, unique=True, null=True, blank=True)),
            ('fname', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('lname', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=25, null=True, blank=True)),
            ('phone_cell', self.gf('django.db.models.fields.CharField')(max_length=25, null=True, blank=True)),
            ('fax', self.gf('django.db.models.fields.CharField')(max_length=25, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
        ))
        db.send_create_signal(u'work_study', ['Contact'])

        # Adding model 'Company'
        db.create_table(u'work_study_company', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('alternative_contract_template', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'work_study', ['Company'])

        # Adding model 'WorkTeam'
        db.create_table(u'work_study_workteam', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('inactive', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('company', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['work_study.Company'], null=True, blank=True)),
            ('team_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('paying', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('funded_by', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('industry_type', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('travel_route', self.gf('django.db.models.fields.CharField')(max_length=50, db_column='train_line', blank=True)),
            ('stop_location', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('am_transport_group', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='workteamset_dropoff', null=True, db_column='dropoff_location_id', to=orm['work_study.PickupLocation'])),
            ('pm_transport_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['work_study.PickupLocation'], null=True, db_column='pickup_location_id', blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('zip', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('directions_to', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('directions_pickup', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('map', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('use_google_maps', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('company_description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('job_description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('time_earliest', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('time_latest', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('time_ideal', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'work_study', ['WorkTeam'])

        # Adding M2M table for field cras on 'WorkTeam'
        db.create_table(u'work_study_workteam_cras', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('workteam', models.ForeignKey(orm[u'work_study.workteam'], null=False)),
            ('cracontact', models.ForeignKey(orm[u'work_study.cracontact'], null=False))
        ))
        db.create_unique(u'work_study_workteam_cras', ['workteam_id', 'cracontact_id'])

        # Adding M2M table for field contacts on 'WorkTeam'
        db.create_table(u'work_study_workteam_contacts', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('workteam', models.ForeignKey(orm[u'work_study.workteam'], null=False)),
            ('contact', models.ForeignKey(orm[u'work_study.contact'], null=False))
        ))
        db.create_unique(u'work_study_workteam_contacts', ['workteam_id', 'contact_id'])

        # Adding model 'PaymentOption'
        db.create_table(u'work_study_paymentoption', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('details', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('cost_per_student', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
        ))
        db.send_create_signal(u'work_study', ['PaymentOption'])

        # Adding model 'StudentFunctionalResponsibility'
        db.create_table(u'work_study_studentfunctionalresponsibility', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'work_study', ['StudentFunctionalResponsibility'])

        # Adding model 'StudentDesiredSkill'
        db.create_table(u'work_study_studentdesiredskill', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'work_study', ['StudentDesiredSkill'])

        # Adding model 'CompContract'
        db.create_table(u'work_study_compcontract', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['work_study.Company'])),
            ('company_name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime.now)),
            ('school_year', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.SchoolYear'], null=True, blank=True)),
            ('number_students', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('payment', self.gf('django.db.models.fields.related.ForeignKey')(default=9999, to=orm['work_study.PaymentOption'], null=True, blank=True)),
            ('student_functional_responsibilities_other', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('student_desired_skills_other', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('student_leave', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('student_leave_lunch', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('student_leave_errands', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('student_leave_other', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('signed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('contract_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('ip_address', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True, blank=True)),
        ))
        db.send_create_signal(u'work_study', ['CompContract'])

        # Adding M2M table for field student_functional_responsibilities on 'CompContract'
        db.create_table(u'work_study_compcontract_student_functional_responsibilities', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('compcontract', models.ForeignKey(orm[u'work_study.compcontract'], null=False)),
            ('studentfunctionalresponsibility', models.ForeignKey(orm[u'work_study.studentfunctionalresponsibility'], null=False))
        ))
        db.create_unique(u'work_study_compcontract_student_functional_responsibilities', ['compcontract_id', 'studentfunctionalresponsibility_id'])

        # Adding M2M table for field student_desired_skills on 'CompContract'
        db.create_table(u'work_study_compcontract_student_desired_skills', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('compcontract', models.ForeignKey(orm[u'work_study.compcontract'], null=False)),
            ('studentdesiredskill', models.ForeignKey(orm[u'work_study.studentdesiredskill'], null=False))
        ))
        db.create_unique(u'work_study_compcontract_student_desired_skills', ['compcontract_id', 'studentdesiredskill_id'])

        # Adding model 'Personality'
        db.create_table(u'work_study_personality', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(unique=True, max_length=4)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'work_study', ['Personality'])

        # Adding model 'Handout33'
        db.create_table(u'work_study_handout33', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('like', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'work_study', ['Handout33'])

        # Adding model 'StudentWorkerRoute'
        db.create_table(u'work_study_studentworkerroute', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
        ))
        db.send_create_signal(u'work_study', ['StudentWorkerRoute'])

        # Adding model 'StudentWorker'
        db.create_table(u'work_study_studentworker', (
            (u'student_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['sis.Student'], unique=True, primary_key=True)),
            ('day', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('transport_exception', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('work_permit_no', self.gf('ecwsp.sis.helper_functions.CharNullField')(max_length=10, unique=True, null=True, blank=True)),
            ('placement', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['work_study.WorkTeam'], null=True, blank=True)),
            ('school_pay_rate', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=2, blank=True)),
            ('student_pay_rate', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=2, blank=True)),
            ('primary_contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['work_study.Contact'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('personality_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['work_study.Personality'], null=True, blank=True)),
            ('adp_number', self.gf('django.db.models.fields.CharField')(max_length=5, blank=True)),
            ('am_route', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='am_student_set', null=True, to=orm['work_study.StudentWorkerRoute'])),
            ('pm_route', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='pm_student_set', null=True, to=orm['work_study.StudentWorkerRoute'])),
        ))
        db.send_create_signal(u'work_study', ['StudentWorker'])

        # Adding M2M table for field handout33 on 'StudentWorker'
        db.create_table(u'work_study_studentworker_handout33', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('studentworker', models.ForeignKey(orm[u'work_study.studentworker'], null=False)),
            ('handout33', models.ForeignKey(orm[u'work_study.handout33'], null=False))
        ))
        db.create_unique(u'work_study_studentworker_handout33', ['studentworker_id', 'handout33_id'])

        # Adding model 'Survey'
        db.create_table(u'work_study_survey', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('survey', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['work_study.StudentWorker'])),
            ('company', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['work_study.WorkTeam'], null=True, blank=True)),
            ('question', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('answer', self.gf('django.db.models.fields.CharField')(max_length=510, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'work_study', ['Survey'])

        # Adding model 'CompanyHistory'
        db.create_table(u'work_study_companyhistory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['work_study.StudentWorker'])),
            ('placement', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['work_study.WorkTeam'])),
            ('date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime.now)),
            ('fired', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'work_study', ['CompanyHistory'])

        # Adding unique constraint on 'CompanyHistory', fields ['student', 'placement', 'date']
        db.create_unique(u'work_study_companyhistory', ['student_id', 'placement_id', 'date'])

        # Adding model 'PresetComment'
        db.create_table(u'work_study_presetcomment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'work_study', ['PresetComment'])

        # Adding model 'StudentInteraction'
        db.create_table(u'work_study_studentinteraction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reported_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('comments', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'work_study', ['StudentInteraction'])

        # Adding M2M table for field student on 'StudentInteraction'
        db.create_table(u'work_study_studentinteraction_student', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('studentinteraction', models.ForeignKey(orm[u'work_study.studentinteraction'], null=False)),
            ('studentworker', models.ForeignKey(orm[u'work_study.studentworker'], null=False))
        ))
        db.create_unique(u'work_study_studentinteraction_student', ['studentinteraction_id', 'studentworker_id'])

        # Adding M2M table for field preset_comment on 'StudentInteraction'
        db.create_table(u'work_study_studentinteraction_preset_comment', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('studentinteraction', models.ForeignKey(orm[u'work_study.studentinteraction'], null=False)),
            ('presetcomment', models.ForeignKey(orm[u'work_study.presetcomment'], null=False))
        ))
        db.create_unique(u'work_study_studentinteraction_preset_comment', ['studentinteraction_id', 'presetcomment_id'])

        # Adding M2M table for field companies on 'StudentInteraction'
        db.create_table(u'work_study_studentinteraction_companies', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('studentinteraction', models.ForeignKey(orm[u'work_study.studentinteraction'], null=False)),
            ('workteam', models.ForeignKey(orm[u'work_study.workteam'], null=False))
        ))
        db.create_unique(u'work_study_studentinteraction_companies', ['studentinteraction_id', 'workteam_id'])

        # Adding model 'TimeSheetPerformanceChoice'
        db.create_table(u'work_study_timesheetperformancechoice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('rank', self.gf('django.db.models.fields.IntegerField')(default=6L, unique=True)),
        ))
        db.send_create_signal(u'work_study', ['TimeSheetPerformanceChoice'])

        # Adding model 'TimeSheet'
        db.create_table(u'work_study_timesheet', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['work_study.StudentWorker'])),
            ('for_pay', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('make_up', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('company', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['work_study.WorkTeam'])),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('time_in', self.gf('django.db.models.fields.TimeField')()),
            ('time_lunch', self.gf('django.db.models.fields.TimeField')()),
            ('time_lunch_return', self.gf('django.db.models.fields.TimeField')()),
            ('time_out', self.gf('django.db.models.fields.TimeField')()),
            ('hours', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=4, decimal_places=2, blank=True)),
            ('school_pay_rate', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=2, blank=True)),
            ('student_pay_rate', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=2, blank=True)),
            ('school_net', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=6, decimal_places=2, blank=True)),
            ('student_net', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=6, decimal_places=2, blank=True)),
            ('approved', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('student_accomplishment', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('performance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['work_study.TimeSheetPerformanceChoice'], null=True, blank=True)),
            ('supervisor_comment', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('show_student_comments', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('supervisor_key', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('cra_email_sent', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'work_study', ['TimeSheet'])

        # Adding model 'AttendanceFee'
        db.create_table(u'work_study_attendancefee', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'work_study', ['AttendanceFee'])

        # Adding model 'AttendanceReason'
        db.create_table(u'work_study_attendancereason', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'work_study', ['AttendanceReason'])

        # Adding model 'Attendance'
        db.create_table(u'work_study_attendance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('student', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['work_study.StudentWorker'])),
            ('absence_date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime.now)),
            ('tardy', self.gf('django.db.models.fields.CharField')(default='P', max_length=1)),
            ('tardy_time_in', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('makeup_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('fee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['work_study.AttendanceFee'], null=True, blank=True)),
            ('paid', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=2, blank=True)),
            ('billed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('reason', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['work_study.AttendanceReason'], null=True, blank=True)),
            ('half_day', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('waive', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('notes', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('sis_attendance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['attendance.StudentAttendance'], null=True, on_delete=models.SET_NULL, blank=True)),
        ))
        db.send_create_signal(u'work_study', ['Attendance'])

        # Adding model 'ClientVisit'
        db.create_table(u'work_study_clientvisit', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dol', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime.now)),
            ('student_worker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['work_study.StudentWorker'], null=True, blank=True)),
            ('cra', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['work_study.CraContact'], null=True, blank=True)),
            ('company', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['work_study.WorkTeam'])),
            ('follow_up_of', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['work_study.ClientVisit'], null=True, blank=True)),
            ('attendance_and_punctuality', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('attitude_and_motivation', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('productivity_and_time_management', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('ability_to_learn_new_tasks', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('professional_appearance', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('interaction_with_coworkers', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('initiative_and_self_direction', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('accuracy_and_attention_to_detail', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('organizational_skills', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('observations', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('supervisor_comments', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('student_comments', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('job_description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('work_environment', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('notify_mentors', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'work_study', ['ClientVisit'])

        # Adding M2M table for field supervisor on 'ClientVisit'
        db.create_table(u'work_study_clientvisit_supervisor', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('clientvisit', models.ForeignKey(orm[u'work_study.clientvisit'], null=False)),
            ('contact', models.ForeignKey(orm[u'work_study.contact'], null=False))
        ))
        db.create_unique(u'work_study_clientvisit_supervisor', ['clientvisit_id', 'contact_id'])

        # Adding model 'MessageToSupervisor'
        db.create_table(u'work_study_messagetosupervisor', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message', self.gf('ckeditor.fields.RichTextField')()),
            ('start_date', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
            ('end_date', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
        ))
        db.send_create_signal(u'work_study', ['MessageToSupervisor'])


    def backwards(self, orm):
        # Removing unique constraint on 'CompanyHistory', fields ['student', 'placement', 'date']
        db.delete_unique(u'work_study_companyhistory', ['student_id', 'placement_id', 'date'])

        # Deleting model 'CraContact'
        db.delete_table(u'work_study_cracontact')

        # Deleting model 'PickupLocation'
        db.delete_table(u'work_study_pickuplocation')

        # Deleting model 'Contact'
        db.delete_table(u'work_study_contact')

        # Deleting model 'Company'
        db.delete_table(u'work_study_company')

        # Deleting model 'WorkTeam'
        db.delete_table(u'work_study_workteam')

        # Removing M2M table for field login on 'WorkTeam'
        db.delete_table('work_study_workteam_login')

        # Removing M2M table for field cras on 'WorkTeam'
        db.delete_table('work_study_workteam_cras')

        # Removing M2M table for field contacts on 'WorkTeam'
        db.delete_table('work_study_workteam_contacts')

        # Deleting model 'PaymentOption'
        db.delete_table(u'work_study_paymentoption')

        # Deleting model 'StudentFunctionalResponsibility'
        db.delete_table(u'work_study_studentfunctionalresponsibility')

        # Deleting model 'StudentDesiredSkill'
        db.delete_table(u'work_study_studentdesiredskill')

        # Deleting model 'CompContract'
        db.delete_table(u'work_study_compcontract')

        # Removing M2M table for field student_functional_responsibilities on 'CompContract'
        db.delete_table('work_study_compcontract_student_functional_responsibilities')

        # Removing M2M table for field student_desired_skills on 'CompContract'
        db.delete_table('work_study_compcontract_student_desired_skills')

        # Deleting model 'Personality'
        db.delete_table(u'work_study_personality')

        # Deleting model 'Handout33'
        db.delete_table(u'work_study_handout33')

        # Deleting model 'StudentWorkerRoute'
        db.delete_table(u'work_study_studentworkerroute')

        # Deleting model 'StudentWorker'
        db.delete_table(u'work_study_studentworker')

        # Removing M2M table for field handout33 on 'StudentWorker'
        db.delete_table('work_study_studentworker_handout33')

        # Deleting model 'Survey'
        db.delete_table(u'work_study_survey')

        # Deleting model 'CompanyHistory'
        db.delete_table(u'work_study_companyhistory')

        # Deleting model 'PresetComment'
        db.delete_table(u'work_study_presetcomment')

        # Deleting model 'StudentInteraction'
        db.delete_table(u'work_study_studentinteraction')

        # Removing M2M table for field student on 'StudentInteraction'
        db.delete_table('work_study_studentinteraction_student')

        # Removing M2M table for field preset_comment on 'StudentInteraction'
        db.delete_table('work_study_studentinteraction_preset_comment')

        # Removing M2M table for field companies on 'StudentInteraction'
        db.delete_table('work_study_studentinteraction_companies')

        # Deleting model 'TimeSheetPerformanceChoice'
        db.delete_table(u'work_study_timesheetperformancechoice')

        # Deleting model 'TimeSheet'
        db.delete_table(u'work_study_timesheet')

        # Deleting model 'AttendanceFee'
        db.delete_table(u'work_study_attendancefee')

        # Deleting model 'AttendanceReason'
        db.delete_table(u'work_study_attendancereason')

        # Deleting model 'Attendance'
        db.delete_table(u'work_study_attendance')

        # Deleting model 'ClientVisit'
        db.delete_table(u'work_study_clientvisit')

        # Removing M2M table for field supervisor on 'ClientVisit'
        db.delete_table('work_study_clientvisit_supervisor')

        # Deleting model 'MessageToSupervisor'
        db.delete_table(u'work_study_messagetosupervisor')


    models = {
        u'attendance.attendancestatus': {
            'Meta': {'object_name': 'AttendanceStatus'},
            'absent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'excused': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'half': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'tardy': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'teacher_selectable': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'attendance.studentattendance': {
            'Meta': {'ordering': "('-date', 'student')", 'unique_together': "(('student', 'date', 'status'),)", 'object_name': 'StudentAttendance'},
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'private_notes': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['attendance.AttendanceStatus']"}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'student_attn'", 'to': u"orm['sis.Student']"}),
            'time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'})
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
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
            'Meta': {'object_name': 'Cohort'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_name': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'students': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['sis.Student']", 'null': 'True', 'db_table': "'sis_studentcohort'", 'blank': 'True'})
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
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
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
        u'sis.mdluser': {
            'Meta': {'ordering': "('lname', 'fname')", 'object_name': 'MdlUser'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '360', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'fname': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inactive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lname': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
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
            'Meta': {'ordering': "('lname', 'fname')", 'object_name': 'Student', '_ormbases': [u'sis.MdlUser']},
            'alert': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'alt_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'bday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'cache_cohort': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'cache_cohorts'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['sis.Cohort']"}),
            'cache_gpa': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'class_of_year': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.ClassYear']", 'null': 'True', 'blank': 'True'}),
            'cohorts': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sis.Cohort']", 'symmetrical': 'False', 'through': u"orm['sis.StudentCohort']", 'blank': 'True'}),
            'date_dismissed': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'emergency_contacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sis.EmergencyContact']", 'symmetrical': 'False', 'blank': 'True'}),
            'family_access_users': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'}),
            'family_preferred_language': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.LanguageChoice']", 'null': 'True', 'blank': 'True'}),
            'grad_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'individual_education_program': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'mdluser_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['sis.MdlUser']", 'unique': 'True', 'primary_key': 'True'}),
            'mname': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'parent_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'parent_guardian': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'pic': ('ecwsp.sis.thumbs.ImageWithThumbsField', [], {'blank': 'True', 'max_length': '100', 'null': 'True', 'sizes': '((70, 65), (530, 400))'}),
            'reason_left': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.ReasonLeft']", 'null': 'True', 'blank': 'True'}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'siblings': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sis.Student']", 'symmetrical': 'False', 'blank': 'True'}),
            'ssn': ('django.db.models.fields.CharField', [], {'max_length': '11', 'null': 'True', 'blank': 'True'}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'unique_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.GradeLevel']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        u'sis.studentcohort': {
            'Meta': {'object_name': 'StudentCohort'},
            'cohort': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.Cohort']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.Student']"})
        },
        u'work_study.attendance': {
            'Meta': {'object_name': 'Attendance'},
            'absence_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'billed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'fee': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.AttendanceFee']", 'null': 'True', 'blank': 'True'}),
            'half_day': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'makeup_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'paid': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'reason': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.AttendanceReason']", 'null': 'True', 'blank': 'True'}),
            'sis_attendance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['attendance.StudentAttendance']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.StudentWorker']"}),
            'tardy': ('django.db.models.fields.CharField', [], {'default': "'P'", 'max_length': '1'}),
            'tardy_time_in': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'waive': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'work_study.attendancefee': {
            'Meta': {'object_name': 'AttendanceFee'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        u'work_study.attendancereason': {
            'Meta': {'object_name': 'AttendanceReason'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'work_study.clientvisit': {
            'Meta': {'object_name': 'ClientVisit'},
            'ability_to_learn_new_tasks': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'accuracy_and_attention_to_detail': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'attendance_and_punctuality': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'attitude_and_motivation': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.WorkTeam']"}),
            'cra': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.CraContact']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'dol': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'follow_up_of': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.ClientVisit']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initiative_and_self_direction': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'interaction_with_coworkers': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'job_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'notify_mentors': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'observations': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'organizational_skills': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'productivity_and_time_management': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'professional_appearance': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'student_comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'student_worker': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.StudentWorker']", 'null': 'True', 'blank': 'True'}),
            'supervisor': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['work_study.Contact']", 'null': 'True', 'blank': 'True'}),
            'supervisor_comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'work_environment': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'})
        },
        u'work_study.company': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Company'},
            'alternative_contract_template': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'work_study.companyhistory': {
            'Meta': {'ordering': "('-date',)", 'unique_together': "(('student', 'placement', 'date'),)", 'object_name': 'CompanyHistory'},
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'fired': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'placement': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.WorkTeam']"}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.StudentWorker']"})
        },
        u'work_study.compcontract': {
            'Meta': {'object_name': 'CompContract'},
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.Company']"}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'contract_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'number_students': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'payment': ('django.db.models.fields.related.ForeignKey', [], {'default': '9999', 'to': u"orm['work_study.PaymentOption']", 'null': 'True', 'blank': 'True'}),
            'school_year': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sis.SchoolYear']", 'null': 'True', 'blank': 'True'}),
            'signed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'student_desired_skills': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['work_study.StudentDesiredSkill']", 'null': 'True', 'blank': 'True'}),
            'student_desired_skills_other': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'student_functional_responsibilities': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['work_study.StudentFunctionalResponsibility']", 'null': 'True', 'blank': 'True'}),
            'student_functional_responsibilities_other': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'student_leave': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'student_leave_errands': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'student_leave_lunch': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'student_leave_other': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'work_study.contact': {
            'Meta': {'ordering': "('lname',)", 'object_name': 'Contact'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'fname': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lname': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'phone_cell': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'})
        },
        u'work_study.cracontact': {
            'Meta': {'object_name': 'CraContact'},
            'email': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email_all': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'work_study.handout33': {
            'Meta': {'ordering': "('category', 'like')", 'object_name': 'Handout33'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'like': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'work_study.messagetosupervisor': {
            'Meta': {'object_name': 'MessageToSupervisor'},
            'end_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('ckeditor.fields.RichTextField', [], {}),
            'start_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'})
        },
        u'work_study.paymentoption': {
            'Meta': {'object_name': 'PaymentOption'},
            'cost_per_student': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'details': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'work_study.personality': {
            'Meta': {'ordering': "('type',)", 'object_name': 'Personality'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '4'})
        },
        u'work_study.pickuplocation': {
            'Meta': {'object_name': 'PickupLocation'},
            'directions': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'long_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'work_study.presetcomment': {
            'Meta': {'ordering': "('comment',)", 'object_name': 'PresetComment'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'work_study.studentdesiredskill': {
            'Meta': {'object_name': 'StudentDesiredSkill'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'work_study.studentfunctionalresponsibility': {
            'Meta': {'object_name': 'StudentFunctionalResponsibility'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'work_study.studentinteraction': {
            'Meta': {'object_name': 'StudentInteraction'},
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'companies': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['work_study.WorkTeam']", 'symmetrical': 'False', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'preset_comment': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['work_study.PresetComment']", 'symmetrical': 'False', 'blank': 'True'}),
            'reported_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'student': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['work_study.StudentWorker']", 'symmetrical': 'False', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        u'work_study.studentworker': {
            'Meta': {'ordering': "('inactive', 'lname', 'fname')", 'object_name': 'StudentWorker', '_ormbases': [u'sis.Student']},
            'adp_number': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'}),
            'am_route': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'am_student_set'", 'null': 'True', 'to': u"orm['work_study.StudentWorkerRoute']"}),
            'day': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'handout33': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['work_study.Handout33']", 'null': 'True', 'blank': 'True'}),
            'personality_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.Personality']", 'null': 'True', 'blank': 'True'}),
            'placement': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.WorkTeam']", 'null': 'True', 'blank': 'True'}),
            'pm_route': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pm_student_set'", 'null': 'True', 'to': u"orm['work_study.StudentWorkerRoute']"}),
            'primary_contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.Contact']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'school_pay_rate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'student_pay_rate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            u'student_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['sis.Student']", 'unique': 'True', 'primary_key': 'True'}),
            'transport_exception': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'work_permit_no': ('ecwsp.sis.helper_functions.CharNullField', [], {'max_length': '10', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'work_study.studentworkerroute': {
            'Meta': {'object_name': 'StudentWorkerRoute'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'work_study.survey': {
            'Meta': {'ordering': "('survey', 'student', 'question')", 'object_name': 'Survey'},
            'answer': ('django.db.models.fields.CharField', [], {'max_length': '510', 'blank': 'True'}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.WorkTeam']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.StudentWorker']"}),
            'survey': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'work_study.timesheet': {
            'Meta': {'object_name': 'TimeSheet'},
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.WorkTeam']"}),
            'cra_email_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'for_pay': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hours': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '4', 'decimal_places': '2', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'make_up': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'performance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.TimeSheetPerformanceChoice']", 'null': 'True', 'blank': 'True'}),
            'school_net': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'school_pay_rate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'show_student_comments': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.StudentWorker']"}),
            'student_accomplishment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'student_net': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'student_pay_rate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'supervisor_comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'supervisor_key': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'time_in': ('django.db.models.fields.TimeField', [], {}),
            'time_lunch': ('django.db.models.fields.TimeField', [], {}),
            'time_lunch_return': ('django.db.models.fields.TimeField', [], {}),
            'time_out': ('django.db.models.fields.TimeField', [], {})
        },
        u'work_study.timesheetperformancechoice': {
            'Meta': {'ordering': "('rank',)", 'object_name': 'TimeSheetPerformanceChoice'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'rank': ('django.db.models.fields.IntegerField', [], {'default': '6L', 'unique': 'True'})
        },
        u'work_study.workteam': {
            'Meta': {'ordering': "('team_name',)", 'object_name': 'WorkTeam'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'am_transport_group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'workteamset_dropoff'", 'null': 'True', 'db_column': "'dropoff_location_id'", 'to': u"orm['work_study.PickupLocation']"}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.Company']", 'null': 'True', 'blank': 'True'}),
            'company_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'contacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['work_study.Contact']", 'symmetrical': 'False', 'blank': 'True'}),
            'cras': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['work_study.CraContact']", 'null': 'True', 'blank': 'True'}),
            'directions_pickup': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'directions_to': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'funded_by': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inactive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'industry_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'job_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'login': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'}),
            'map': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'paying': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'pm_transport_group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['work_study.PickupLocation']", 'null': 'True', 'db_column': "'pickup_location_id'", 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'stop_location': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'team_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'time_earliest': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'time_ideal': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'time_latest': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'travel_route': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "'train_line'", 'blank': 'True'}),
            'use_google_maps': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        }
    }

    complete_apps = ['work_study']
