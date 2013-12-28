# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
            ('sis','0001_initial'),
    )
    def forwards(self, orm):
        # Adding model 'Benchmark'
        db.create_table(u'benchmarks_benchmark', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=700)),
            ('year', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sis.GradeLevel'], null=True, blank=True)),
        ))
        db.send_create_signal(u'benchmarks', ['Benchmark'])

        # Adding M2M table for field measurement_topics on 'Benchmark'
        m2m_table_name = db.shorten_name(u'benchmarks_benchmark_measurement_topics')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('benchmark', models.ForeignKey(orm[u'benchmarks.benchmark'], null=False)),
            ('measurementtopic', models.ForeignKey(orm[u'benchmarks.measurementtopic'], null=False))
        ))
        db.create_unique(m2m_table_name, ['benchmark_id', 'measurementtopic_id'])

        # Adding model 'Department'
        db.create_table(u'benchmarks_department', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'benchmarks', ['Department'])

        # Adding model 'MeasurementTopic'
        db.create_table(u'benchmarks_measurementtopic', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('department', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['benchmarks.Department'], null=True, blank=True)),
        ))
        db.send_create_signal(u'benchmarks', ['MeasurementTopic'])

        # Adding unique constraint on 'MeasurementTopic', fields ['name', 'department']
        db.create_unique(u'benchmarks_measurementtopic', ['name', 'department_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'MeasurementTopic', fields ['name', 'department']
        db.delete_unique(u'benchmarks_measurementtopic', ['name', 'department_id'])

        # Deleting model 'Benchmark'
        db.delete_table(u'benchmarks_benchmark')

        # Removing M2M table for field measurement_topics on 'Benchmark'
        db.delete_table(db.shorten_name(u'benchmarks_benchmark_measurement_topics'))

        # Deleting model 'Department'
        db.delete_table(u'benchmarks_department')

        # Deleting model 'MeasurementTopic'
        db.delete_table(u'benchmarks_measurementtopic')


    models = {
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
        u'sis.gradelevel': {
            'Meta': {'ordering': "('id',)", 'object_name': 'GradeLevel'},
            'id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150'})
        }
    }

    complete_apps = ['benchmarks']
