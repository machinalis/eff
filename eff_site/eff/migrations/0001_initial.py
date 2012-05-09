# -*- coding: utf-8 -*-
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

        # Adding model 'ProjectAssoc'
        db.create_table('eff_projectassoc', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eff.Project'])),
            ('member', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eff.UserProfile'])),
            ('client_rate', self.gf('django.db.models.fields.DecimalField')(max_digits=19, decimal_places=2)),
            ('user_rate', self.gf('django.db.models.fields.DecimalField')(max_digits=19, decimal_places=2)),
            ('from_date', self.gf('django.db.models.fields.DateField')()),
            ('to_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('eff', ['ProjectAssoc'])

        # Adding model 'Project'
        db.create_table('eff_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('billable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('external_id', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eff.Client'])),
            ('billing_type', self.gf('django.db.models.fields.CharField')(default='HOUR', max_length=8)),
            ('fixed_price', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=2, blank=True)),
        ))
        db.send_create_signal('eff', ['Project'])

        # Adding model 'Dump'
        db.create_table('eff_dump', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('creator', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eff.ExternalSource'], null=True)),
        ))
        db.send_create_signal('eff', ['Dump'])

        # Adding model 'TimeLog'
        db.create_table('eff_timelog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eff.Project'])),
            ('task_name', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('hours_booked', self.gf('django.db.models.fields.FloatField')()),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('dump', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eff.Dump'])),
        ))
        db.send_create_signal('eff', ['TimeLog'])

        # Adding model 'UserProfile'
        db.create_table('eff_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
            ('personal_email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('phone_number', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
        ))
        db.send_create_signal('eff', ['UserProfile'])

        # Adding model 'ExternalId'
        db.create_table('eff_externalid', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('login', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eff.ExternalSource'], null=True)),
            ('userprofile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eff.UserProfile'])),
        ))
        db.send_create_signal('eff', ['ExternalId'])

        # Adding model 'ExternalSource'
        db.create_table('eff_externalsource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('fetch_url', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('csv_directory', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('csv_filename', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('eff', ['ExternalSource'])

        # Adding model 'Wage'
        db.create_table('eff_wage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('amount_per_hour', self.gf('django.db.models.fields.DecimalField')(max_digits=19, decimal_places=2)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('eff', ['Wage'])

        # Adding unique constraint on 'Wage', fields ['user', 'date']
        db.create_unique('eff_wage', ['user_id', 'date'])

        # Adding model 'Currency'
        db.create_table('eff_currency', (
            ('ccy_code', self.gf('django.db.models.fields.CharField')(max_length=3, primary_key=True)),
            ('ccy_symbol', self.gf('django.db.models.fields.CharField')(max_length=5, null=True, blank=True)),
        ))
        db.send_create_signal('eff', ['Currency'])

        # Adding model 'Client'
        db.create_table('eff_client', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('billing_email_address', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('contact_email_address', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('currency', self.gf('django.db.models.fields.related.ForeignKey')(default='USD', to=orm['eff.Currency'])),
            ('external_source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eff.ExternalSource'])),
            ('external_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('eff', ['Client'])

    def backwards(self, orm):
        # Removing unique constraint on 'Wage', fields ['user', 'date']
        db.delete_unique('eff_wage', ['user_id', 'date'])

        # Removing unique constraint on 'AvgHours', fields ['user', 'date']
        db.delete_unique('eff_avghours', ['user_id', 'date'])

        # Deleting model 'AvgHours'
        db.delete_table('eff_avghours')

        # Deleting model 'ProjectAssoc'
        db.delete_table('eff_projectassoc')

        # Deleting model 'Project'
        db.delete_table('eff_project')

        # Deleting model 'Dump'
        db.delete_table('eff_dump')

        # Deleting model 'TimeLog'
        db.delete_table('eff_timelog')

        # Deleting model 'UserProfile'
        db.delete_table('eff_userprofile')

        # Deleting model 'ExternalId'
        db.delete_table('eff_externalid')

        # Deleting model 'ExternalSource'
        db.delete_table('eff_externalsource')

        # Deleting model 'Wage'
        db.delete_table('eff_wage')

        # Deleting model 'Currency'
        db.delete_table('eff_currency')

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
        'eff.avghours': {
            'Meta': {'ordering': "['date', 'user']", 'unique_together': "(('user', 'date'),)", 'object_name': 'AvgHours'},
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
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'default': "'USD'", 'to': "orm['eff.Currency']"}),
            'external_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'external_source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eff.ExternalSource']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'eff.currency': {
            'Meta': {'object_name': 'Currency'},
            'ccy_code': ('django.db.models.fields.CharField', [], {'max_length': '3', 'primary_key': 'True'}),
            'ccy_symbol': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'})
        },
        'eff.dump': {
            'Meta': {'object_name': 'Dump'},
            'creator': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eff.ExternalSource']", 'null': 'True'})
        },
        'eff.externalid': {
            'Meta': {'object_name': 'ExternalId'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'login': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eff.ExternalSource']", 'null': 'True'}),
            'userprofile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eff.UserProfile']"})
        },
        'eff.externalsource': {
            'Meta': {'object_name': 'ExternalSource'},
            'csv_directory': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'csv_filename': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'fetch_url': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        'eff.project': {
            'Meta': {'object_name': 'Project'},
            'billable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'billing_type': ('django.db.models.fields.CharField', [], {'default': "'HOUR'", 'max_length': '8'}),
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eff.Client']"}),
            'external_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'fixed_price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '2', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['eff.UserProfile']", 'through': "orm['eff.ProjectAssoc']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'eff.projectassoc': {
            'Meta': {'object_name': 'ProjectAssoc'},
            'client_rate': ('django.db.models.fields.DecimalField', [], {'max_digits': '19', 'decimal_places': '2'}),
            'from_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eff.UserProfile']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eff.Project']"}),
            'to_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'user_rate': ('django.db.models.fields.DecimalField', [], {'max_digits': '19', 'decimal_places': '2'})
        },
        'eff.timelog': {
            'Meta': {'object_name': 'TimeLog'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'dump': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eff.Dump']"}),
            'hours_booked': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eff.Project']"}),
            'task_name': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'eff.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'personal_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'eff.wage': {
            'Meta': {'ordering': "['date', 'user']", 'unique_together': "(('user', 'date'),)", 'object_name': 'Wage'},
            'amount_per_hour': ('django.db.models.fields.DecimalField', [], {'max_digits': '19', 'decimal_places': '2'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['eff']