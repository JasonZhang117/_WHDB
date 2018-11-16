from django import forms
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from A_dbms.models import Employees


# ------------------------------自定义-------------------------------#
class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password',
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation',
                                widget=forms.PasswordInput)

    class Meta:
        model = Employees
        fields = ('email', 'name')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("密码不匹配")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        # 把明文根据算法改成密文
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Employees
        fields = ('email', 'password', 'name',
                  'is_active', 'is_superuser')

    def clean_password(self):
        '''Regardless of what the user provides, return the initial value.
        This is done here, rather than on the field, because the field does not have access to the initial value.'''
        return self.initial["password"]


# ------------------------------自定义-------------------------------#
class EmployeesAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm
    '''The fields to be used in displaying the User model.
    These override the definitions on the base UserAdmin that reference specific fields on auth.User.'''
    list_display = ('email', 'name', 'num', 'is_superuser')
    list_filter = ('is_superuser',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name',)}),
        ('Permissions',
         {'fields': ('is_active', 'is_staff',
                     'is_superuser', 'job',
                     'user_permissions', 'groups')}),)
    '''add_fieldsets is not a standard ModelAdmin attribute.
    UserAdmin overrides get_fieldsets to use this attribute when creating a user.'''
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'num',
                       'password1', 'password2')}),)
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ("job", 'user_permissions', 'groups')
