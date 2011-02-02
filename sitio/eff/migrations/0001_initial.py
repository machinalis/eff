# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'AvgHours'
        db.create_table('eff_avghours', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('hours', self.gf('django.db.models.fields.FloatField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('eff', ['AvgHours'])

        # Adding unique constraint on 'AvgHours', fields ['user', 'date']
        db.create_unique('eff_avghours', ['user_id', 'date'])

        # Adding model 'Project'
        db.create_table('eff_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('billable', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('log', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eff.Log'])),
            ('external_source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eff.ExternalSource'])),
            ('external_id', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eff.Client'], null=True)),
        ))
        db.send_create_signal('eff', ['Project'])

        # Adding model 'Log'
        db.create_table('eff_log', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('log_type', self.gf('django.db.models.fields.CharField')(max_length=15)),
        ))
        db.send_create_signal('eff', ['Log'])

        # Adding model 'CsvLog'
        db.create_table('eff_csvlog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eff.Project'])),
            ('task_name', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('time_on_task', self.gf('django.db.models.fields.FloatField')()),
            ('summary', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('eff', ['CsvLog'])

        # Adding model 'UserProfile'
        db.create_table('eff_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
            ('prot_login', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('prot_name', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('personal_email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('phone_number', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
        ))
        db.send_create_signal('eff', ['UserProfile'])

        # Adding model 'ExternalSource'
        db.create_table('eff_externalsource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('fetch_url', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('csv_directory', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('csv_filename', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('eff', ['ExternalSource'])

        # Adding model 'Wage'
        db.create_table('eff_wage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('amount_per_hour', self.gf('django.db.models.fields.FloatField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('eff', ['Wage'])

        # Adding unique constraint on 'Wage', fields ['user', 'date']
        db.create_unique('eff_wage', ['user_id', 'date'])

        # Adding model 'Client'
        db.create_table('eff_client', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, db_index=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('billing_email_address', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('contact_email_address', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
        ))
        db.send_create_signal('eff', ['Client'])


    def backwards(self, orm):
        
        # Deleting model 'AvgHours'
        db.delete_table('eff_avghours')

        # Removing unique constraint on 'AvgHours', fields ['user', 'date']
        db.delete_unique('eff_avghours', ['user_id', 'date'])

        # Deleting model 'Project'
        db.delete_table('eff_project')

        # Deleting model 'Log'
        db.delete_table('eff_log')

        # Deleting model 'CsvLog'
        db.delete_table('eff_csvlog')

        # Deleting model 'UserProfile'
        db.delete_table('eff_userprofile')

        # Deleting model 'ExternalSource'
        db.delete_table('eff_externalsource')

        # Deleting model 'Wage'
        db.delete_table('eff_wage')

        # Removing unique constraint on 'Wage', fields ['user', 'date']
        db.delete_unique('eff_wage', ['user_id', 'date'])

        # Deleting model 'Client'
        db.delete_table('eff_client')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'eff.avghours': {
            'Meta': {'unique_together': "(('user', 'date'),)", 'object_name': 'AvgHours'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'hours': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'eff.client': {
            'Meta': {'object_name': 'Client'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'billing_email_address': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'contact_email_address': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'eff.csvlog': {
            'Meta': {'object_name': 'CsvLog'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eff.Project']"}),
            'summary': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'task_name': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'time_on_task': ('django.db.models.fields.FloatField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'eff.externalsource': {
            'Meta': {'object_name': 'ExternalSource'},
            'csv_directory': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'csv_filename': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'fetch_url': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        'eff.log': {
            'Meta': {'object_name': 'Log'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'log_type': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        },
        'eff.project': {
            'Meta': {'object_name': 'Project'},
            'billable': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eff.Client']", 'null': 'True'}),
            'external_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'external_source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eff.ExternalSource']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'log': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eff.Log']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'eff.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'personal_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'prot_login': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'prot_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'eff.wage': {
            'Meta': {'unique_together': "(('user', 'date'),)", 'object_name': 'Wage'},
            'amount_per_hour': ('django.db.models.fields.FloatField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['eff']
