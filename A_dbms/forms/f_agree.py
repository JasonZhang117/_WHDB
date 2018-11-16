from django import forms as dform
from django.forms import fields
from django.forms import widgets
import datetime
from .. import models
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError


# -----------------------项目添加-------------------------#
class AgreeAddForm(dform.Form):  # 项目添加
    AGREE_TYP_LIST = [('单笔', '单笔'), ('最高额', '最高额')]
    agree_num = fields.CharField(label='合同编号',
                                 label_suffix="：")
    article_id = fields.IntegerField(label="纪要",
                                     label_suffix="：",
                                     widget=widgets.Select())
    branch_id = fields.IntegerField(label="银行",
                                    label_suffix="：",
                                    widget=widgets.Select())
    agree_typ = fields.CharField(
        label='合同类型',
        label_suffix="：",
        widget=widgets.Select(choices=AGREE_TYP_LIST))
    agree_amount = fields.FloatField(label="合同金额",
                                     label_suffix="：")

    def __init__(self, *args, **kwargs):
        super(AgreeAddForm, self).__init__(*args, **kwargs)
        self.fields['article_id'].widget.choices = \
            models.Articles.objects.filter(article_state=6).\
                values_list('id', 'summary_num').\
                order_by('summary_num')
        self.fields['branch_id'].widget.choices = \
            models.Branches.objects.filter(branch_state=1).\
                values_list('id', 'name').order_by('name')
