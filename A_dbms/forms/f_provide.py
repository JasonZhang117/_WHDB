from django import forms as dform
from django.forms import fields, widgets
from .. import models


# -----------------------放款通知添加-------------------------#
class FormNotifyAdd(dform.ModelForm):
    class Meta:
        model = models.Notify
        fields = ['notify_money', 'notify_date']


# -----------------------放款添加-------------------------#
class FormProvideAdd(dform.ModelForm):
    class Meta:
        model = models.Provides
        fields = ['provide_typ', 'provide_money', 'provide_date', 'due_date']
