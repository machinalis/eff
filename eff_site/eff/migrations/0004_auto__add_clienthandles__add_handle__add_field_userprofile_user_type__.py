# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ClientHandles'
        db.create_table('eff_clienthandles', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('handle', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eff.Handle'])),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eff.UserProfile'])),
            ('address', self.gf('django.db.models.fields.CharField')(default='', max_length=100)),
        ))
        db.send_create_signal('eff', ['ClientHandles'])

        # Adding model 'Handle'
        db.create_table('eff_handle', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('protocol', self.gf('django.db.models.fields.CharField')(default='', max_length=100)),
            ('sort_name', self.gf('django.db.models.fields.CharField')(default='', max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', max_length=200, blank=True)),
        ))
        db.send_create_signal('eff', ['Handle'])

        # Adding field 'UserProfile.user_type'
        db.add_column('eff_userprofile', 'user_type',
                      self.gf('django.db.models.fields.CharField')(default='Default', max_length=50),
                      keep_default=False)

        # Adding field 'UserProfile.company'
        db.add_column('eff_userprofile', 'company',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eff.Client'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.job_position'
        db.add_column('eff_userprofile', 'job_position',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting model 'ClientHandles'
        db.delete_table('eff_clienthandles')

        # Deleting model 'Handle'
        db.delete_table('eff_handle')

        # Deleting field 'UserProfile.user_type'
        db.delete_column('eff_userprofile', 'user_type')

        # Deleting field 'UserProfile.company'
        db.delete_column('eff_userprofile', 'company_id')

        # Deleting field 'UserProfile.job_position'
        db.delete_column('eff_userprofile', 'job_position')

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
            'hours': ('django.db.models.fields.DecimalField', [], {'max_digits': '19', 'decimal_places': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'eff.client': {
            'Meta': {'ordering': "['name']", 'object_name': 'Client'},
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
        'eff.clienthandles': {
            'Meta': {'object_name': 'ClientHandles'},
            'address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eff.UserProfile']"}),
            'handle': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eff.Handle']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'eff.currency': {
            'Meta': {'ordering': "['ccy_code']", 'object_name': 'Currency'},
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
        'eff.handle': {
            'Meta': {'object_name': 'Handle'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'protocol': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'sort_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'})
        },
        'eff.project': {
            'Meta': {'ordering': "['client', 'name']", 'object_name': 'Project'},
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
            'Meta': {'ordering': "['project', 'member']", 'object_name': 'ProjectAssoc'},
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
            'hours_booked': ('django.db.models.fields.DecimalField', [], {'max_digits': '19', 'decimal_places': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eff.Project']"}),
            'task_name': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'eff.userprofile': {
            'Meta': {'ordering': "['user__first_name']", 'object_name': 'UserProfile'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eff.Client']", 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'handles': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['eff.Handle']", 'through': "orm['eff.ClientHandles']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_position': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'personal_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'user_type': ('django.db.models.fields.CharField', [], {'default': "'Default'", 'max_length': '50'}),
            'watches': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'watched_by'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.User']"})
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