from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as OldUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.admin import FlatPageAdmin
from django.core.urlresolvers import reverse

from tinymce.widgets import TinyMCE

from .models import *


#########
# forms #
#########

class UserChangeForm(forms.ModelForm):
    """
    A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField(help_text="Raw passwords are not stored, so there is no way to see "
                "this user's password, but you can change the password "
                "using <a href=\"password/\">this form</a>.")

    def clean_id(self):
        return self.initial['id']

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

    class Meta:
        model = User
        exclude = (
            'date_joined',
            'last_login',
        )

class UserCreationForm(forms.Form):
    """
    A form that creates a user, with no privileges, from the given email and password.
    used by the User admin
    """
    error_messages = {
        'password_mismatch': "The two password fields didn't match.",
    }
    email = forms.EmailField(
        max_length=255,
        help_text="Required. Must be a valid email address",
    )
    name = forms.CharField(
        max_length=255,
        help_text="Name of the User",
    )
    password1 = forms.CharField(
        label= 'Password',
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput,
        help_text="Enter the same password as above, for verification."
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'])
        return password2

    def save(self, **kwargs):
        return User.objects.create_user(
            self.cleaned_data.get('email'),
            self.cleaned_data.get('password1'),
        )

    def save_m2m(self, *args, **kwargs):
        """placeholder for admin form"""
        pass

###########
# inlines #
###########

class ProfileInline(admin.StackedInline):
    model = Profile

###############
# admin stuff #
###############

class UserAdmin(OldUserAdmin):
    """inherit from the standard User admin and add in our magic"""
    form = UserChangeForm
    add_form = UserCreationForm

    inlines = [ProfileInline,]
    list_display = ('email', 'name', 'is_staff')
    list_filter = ('is_staff', 'is_active',)
    ordering = ['email']
    search_fields = ('email', 'name',)
    fieldsets = (
        (None, { 'fields': ('email', 'name', 'password',) }),
        ('Permissions', { 'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions') }),
        ('Companies', { 'fields': ('groups',) }),
    )
    add_fieldsets = (
        (None, {
            'fields': ('email', 'name', 'password1', 'password2')}
        ),
    )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'user_permissions':
            content_type = ContentType.objects.get(app_label='core', model='opinion')
            kwargs['queryset'] = Permission.objects.filter(content_type=content_type).exclude(codename__in=('add_opinion', 'change_opinion', 'delete_opinion')).all()
        return super(UserAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

admin.site.register(User, UserAdmin)

### handle the django-tinymce work here
class TinyMCEFlatPageAdmin(FlatPageAdmin):
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'content':
            return db_field.formfield(widget=TinyMCE(
                attrs={'cols': 80, 'rows': 30},
                mce_attrs={'external_link_list_url': reverse('tinymce.views.flatpages_link_list')},
            ))
        return super(TinyMCEFlatPageAdmin, self).formfield_for_dbfield(db_field, **kwargs)

admin.site.unregister(FlatPage)
admin.site.register(FlatPage, TinyMCEFlatPageAdmin)
