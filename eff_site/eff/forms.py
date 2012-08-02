# -*- coding: utf-8 -*-
# Copyright 2009 - 2011 Machinalis: http://www.machinalis.com/
#
# This file is part of Eff.
#
# Eff is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Eff is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Eff.  If not, see <http://www.gnu.org/licenses/>.

from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from django.forms.util import ErrorList

from eff_site.eff.models import UserProfile, Client, AvgHours, Wage


class AvgHoursForm(forms.Form):
    ah_date = forms.DateField(required=True)
    hours = forms.IntegerField(required=True)


class EffQueryForm(forms.Form):
    from_date = forms.DateField(required=True,
                                widget=forms.DateInput,
                                label='Desde')
    to_date = forms.DateField(required=True,
                              widget=forms.DateInput,
                              label='Hasta')

    def clean_to_date(self):
        cleaned_data = super(EffQueryForm, self).clean()
        from_date = cleaned_data.get('from_date')
        to_date = cleaned_data.get('to_date')
        if to_date < from_date:
            raise forms.ValidationError("This date should be greater")

        return to_date


class UserProfileForm(ModelForm):
    """ Combines data from UserProfile """

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        try:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
        except User.DoesNotExist:
            pass

    def save(self, *args, **kwargs):
        u = self.instance.user
        u.first_name = self.cleaned_data['first_name']
        u.last_name = self.cleaned_data['last_name']
        u.save()
        profile = super(UserProfileForm, self).save(*args, **kwargs)
        return profile

    class Meta:
        model = UserProfile
        fields = ('first_name', 'last_name', 'personal_email', 'address',
                  'city', 'state', 'country', 'phone_number',
                  'receive_report_email')

    first_name = forms.CharField(required=False, label='Nombre')
    last_name = forms.CharField(required=False, label='Apellido')

    personal_email = forms.EmailField(required=False, label='Email Personal')
    address = forms.CharField(required=False, label='Dirección')
    city = forms.CharField(required=False, label='Ciudad')
    state = forms.CharField(required=False, label='Provincia')
    country = forms.CharField(required=False, label='Pais')
    phone_number = forms.IntegerField(required=False, label='Telefono')


class ClientUserProfileForm(ModelForm):
    first_name = forms.CharField(required=False, label='First name')
    last_name = forms.CharField(required=False, label='Last name')
    email = forms.EmailField(required=True, label='Email', max_length=254)

    def __init__(self, *args, **kwargs):
        super(ClientUserProfileForm, self).__init__(*args, **kwargs)
        try:
            self.initial['first_name'] = self.instance.user.first_name
            self.initial['last_name'] = self.instance.user.last_name
            self.initial['email'] = self.instance.user.email
        except User.DoesNotExist:
            pass

    def clean_first_name(self):
        data = self.cleaned_data['first_name']
        if "" == data:
            raise forms.ValidationError("This Field is required")
        return data

    def clean_last_name(self):
        data = self.cleaned_data['last_name']
        if "" == data:
            raise forms.ValidationError("This Field is required")
        return data

    def clean_email(self):
        # Get current user's username
        username = self.instance.user.username
        email = self.cleaned_data.get('email')
        users = User.objects.filter(email=email).exclude(username=username)
        if email and users.count():
            raise forms.ValidationError(u'Email address must be unique.')
        return email

    def save(self, *args, **kwargs):
        u = self.instance.user
        u.first_name = self.cleaned_data['first_name']
        u.last_name = self.cleaned_data['last_name']
        u.email = self.cleaned_data['email']
        u.save()
        profile = super(ClientUserProfileForm, self).save(*args, **kwargs)
        return profile

    class Meta:
        model = UserProfile
        fields = ('first_name', 'last_name', 'job_position', 'email',
                  'phone_number')


class UsersChangeProfileForm(UserProfileForm):
    """ Users profile change  """
    user = forms.ModelChoiceField(queryset=User.objects.all(),
                                  empty_label="----")

    class Meta:
        model = UserProfile
        fields = ('user', 'first_name', 'last_name', 'personal_email',
                  'address', 'city', 'state', 'country', 'phone_number',)


class UserPassChangeForm(forms.Form):
    """ Users password change """
    user = forms.ModelChoiceField(queryset=User.objects.all(),
                                  empty_label="----")
    password = forms.CharField(max_length=100,
                               widget=forms.PasswordInput,
                               label='New password',
                               required=False)
    password2 = forms.CharField(max_length=100,
                                widget=forms.PasswordInput,
                                label='Confirm password',
                                required=False)

    def clean(self):
        password2 = self.cleaned_data.get('password2')
        password = self.cleaned_data.get('password')

        if password is None and password2 is None:
            return self.cleaned_data

        if password is not None and password2 != password:
            raise forms.ValidationError('The two passwords do not match.')

        return self.cleaned_data


class UserAddForm(forms.Form):
    """ Add user """
    username = forms.CharField(max_length=100, label='Username')
    password = forms.CharField(max_length=100, widget=forms.PasswordInput,
                               label='Password')
    password2 = forms.CharField(max_length=100, widget=forms.PasswordInput,
                                label='Password confirmation')

    def clean(self):
        password2 = self.cleaned_data.get('password2')
        password = self.cleaned_data.get('password')

        if password is None and password2 is None:
            return self.cleaned_data

        if password is not None and password2 != password:
            raise forms.ValidationError('The two passwords do not match.')

        try:
            if User.objects.get(username=self.cleaned_data.get('username')):
                raise forms.ValidationError('User already exists.')
        except User.DoesNotExist:
            pass
        return self.cleaned_data


class ClientReportForm(EffQueryForm):
    """ Admin to generate client reports """
    client = forms.ModelChoiceField(queryset=Client.objects.all(),
                                    empty_label="----")


class DumpUploadForm(forms.Form):
    csv_file = forms.FileField()

    def clean(self):
        csv_file = self.cleaned_data.get('csv_file')
        if not csv_file:
            return self.cleaned_data
        if csv_file.content_type != 'text/csv':
            raise forms.ValidationError('Only CSV files are allowed.')
        return self.cleaned_data


class AvgHoursModelForm(forms.ModelForm):
    class Meta:
        model = AvgHours
        exclude = ('user',)


class WageModelForm(forms.ModelForm):
    class Meta:
        model = Wage
        exclude = ('user',)


class UserAdminForm(UserCreationForm):
    email = forms.EmailField(required=True, label='E-mail address',
                             max_length=254)
    is_client = forms.BooleanField(required=False, label="Client",
                                   help_text=("Designates whether this user"
                                              "should be treated as a Client."))
    company = forms.ModelChoiceField(required=False,
                                     queryset=Client.objects.all())

    class Meta:
        model = User
        # Needed to define an order (hashed password not shown)
        fields = ('username', 'password1', 'password2', 'is_client', 'company',
                  'first_name', 'last_name', 'email', 'is_staff', 'is_active',
                  'is_superuser', 'last_login', 'date_joined', 'groups',
                  'user_permissions',)

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        try:
            profile = self.instance.get_profile()
            self.fields['is_client'].initial = profile.is_client()
            self.fields['company'].initial = profile.company
        except User.DoesNotExist:
            pass
        except UserProfile.DoesNotExist:
            pass

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        users = User.objects.filter(email=email).exclude(username=username)
        if email and users.count():
            raise forms.ValidationError(u'Email address must be unique.')
        return email

    def clean(self):
        cleaned_data = super(UserAdminForm, self).clean()
        is_client = cleaned_data.get("is_client")
        company = cleaned_data.get("company")

        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")
        errors = False

        if is_client and not company:
            self._errors['company'] = self._errors.get('company', ErrorList())
            self._errors['company'].append("A client user must have Company")
            errors = True
        if is_client and not first_name:
            self._errors['first_name'] = self._errors.get('first_name',
                ErrorList())
            self._errors['first_name'].append("A client user must have First " \
                "name")
            errors = True
        if is_client and not last_name:
            self._errors['last_name'] = self._errors.get('last_name',
                ErrorList())
            self._errors['last_name'].append("A client user must have Last " \
                "name")
            errors = True

        if company and not is_client:
            self._errors['company'] = self._errors.get('company',
                                                       ErrorList())
            self._errors['company'].append("A default user not must have "\
                                           "Company")
            errors = True

        if errors:
            raise forms.ValidationError('Some field are invalid')

        return cleaned_data

    def save(self, *args, **kwargs):
        if self.instance.pk is None:
            # Add new user to Attachment's group
            try:
                group_attachment = Group.objects.get(name='attachments')
                if group_attachment not in self.cleaned_data['groups']:
                    self.cleaned_data['groups'].append(group_attachment)
            except Group.DoesNotExist:
                pass

        kwargs.pop('commit', None)
        user = super(UserCreationForm, self).save(*args, commit=False,
                                                      **kwargs)
        password = self.cleaned_data["password1"]
        if password:
            user.set_password(password)

        user.is_client = self.cleaned_data['is_client']
        if user.is_client:
            user.company = self.cleaned_data['company']
            user.is_client = self.cleaned_data['is_client']
        user.save()
        self.save_m2m(*args, **kwargs)
        return user


class UserAdminChangeForm(UserAdminForm):
    password1 = forms.CharField(label=("Password"), widget=forms.PasswordInput,
                                required=False)
    password2 = forms.CharField(label=("Password confirmation"),
                                widget=forms.PasswordInput, required=False,
                                help_text=("Enter the same password as above, "
                                           "for verification."))

    def clean_username(self):
        return self.cleaned_data["username"]

    def clean_email(self):
        # Get current user's username
        username = self.instance.username
        email = self.cleaned_data.get('email')
        users = User.objects.filter(email=email).exclude(username=username)
        if email and users.count():
            raise forms.ValidationError(u'Email address must be unique.')
        return email
