# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Billing'
        db.create_table('eff_billing', (
            ('comercialdocumentbase_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['eff.ComercialDocumentBase'], unique=True, primary_key=True)),
            ('expire_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('payment_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('eff', ['Billing'])

        # Adding model 'ComercialDocumentBase'
        db.create_table('eff_comercialdocumentbase', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eff.Client'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('concept', self.gf('django.db.models.fields.TextField')()),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=19, decimal_places=2)),
        ))
        db.send_create_signal('eff', ['ComercialDocumentBase'])

        # Adding model 'Payment'
        db.create_table('eff_payment', (
            ('comercialdocumentbase_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['eff.ComercialDocumentBase'], unique=True, primary_key=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='Notified', max_length=20)),
        ))
        db.send_create_signal('eff', ['Payment'])

        # Adding model 'CreditNote'
        db.create_table('eff_creditnote', (
            ('comercialdocumentbase_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['eff.ComercialDocumentBase'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('eff', ['CreditNote'])

    def backwards(self, orm):
        # Deleting model 'Billing'
        db.delete_table('eff_billing')

        # Deleting model 'ComercialDocumentBase'
        db.delete_table('eff_comercialdocumentbase')

        # Deleting model 'Payment'
        db.delete_table('eff_payment')

        # Deleting model 'CreditNote'
        db.delete_table('eff_creditnote')

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
        'eff.billing': {
            'Meta': {'ordering': "['client', '-date']", 'object_name': 'Billing', '_ormbases': ['eff.ComercialDocumentBase']},
            'comercialdocumentbase_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['eff.ComercialDocumentBase']", 'unique': 'True', 'primary_key': 'True'}),
            'expire_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'payment_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'eff.billingemail': {
            'Meta': {'ordering': "['client', 'email_address']", 'object_name': 'BillingEmail'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eff.Client']"}),
            'email_address': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'send_as': ('django.db.models.fields.CharField', [], {'default': "'to'", 'max_length': '3'})
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
        'eff.comercialdocumentbase': {
            'Meta': {'ordering': "['client', '-date']", 'object_name': 'ComercialDocumentBase'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '19', 'decimal_places': '2'}),
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eff.Client']"}),
            'concept': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'eff.creditnote': {
            'Meta': {'ordering': "['client', '-date']", 'object_name': 'CreditNote', '_ormbases': ['eff.ComercialDocumentBase']},
            'comercialdocumentbase_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['eff.ComercialDocumentBase']", 'unique': 'True', 'primary_key': 'True'})
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'protocol': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'})
        },
        'eff.payment': {
            'Meta': {'ordering': "['client', '-date']", 'object_name': 'Payment', '_ormbases': ['eff.ComercialDocumentBase']},
            'comercialdocumentbase_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['eff.ComercialDocumentBase']", 'unique': 'True', 'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'Notified'", 'max_length': '20'})
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
            'receive_report_email': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
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