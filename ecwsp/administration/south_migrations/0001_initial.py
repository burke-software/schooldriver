# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AccessLog'
        db.create_table(u'administration_accesslog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('login', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('ua', self.gf('django.db.models.fields.CharField')(max_length=2000)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('usage', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'administration', ['AccessLog'])

        # Adding model 'Configuration'
        db.create_table(u'administration_configuration', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('value', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('help_text', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'administration', ['Configuration'])

        # Adding model 'Template'
        db.create_table(u'administration_template', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('general_student', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('report_card', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('benchmark_report_card', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('transcript', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'administration', ['Template'])


    def backwards(self, orm):
        # Deleting model 'AccessLog'
        db.delete_table(u'administration_accesslog')

        # Deleting model 'Configuration'
        db.delete_table(u'administration_configuration')

        # Deleting model 'Template'
        db.delete_table(u'administration_template')


    models = {
        u'administration.accesslog': {
            'Meta': {'object_name': 'AccessLog'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'login': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'ua': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'usage': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'administration.configuration': {
            'Meta': {'object_name': 'Configuration'},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'help_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'value': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'administration.template': {
            'Meta': {'object_name': 'Template'},
            'benchmark_report_card': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'general_student': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'report_card': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'transcript': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
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
        }
    }

    complete_apps = ['administration']