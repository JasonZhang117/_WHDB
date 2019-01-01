from django.shortcuts import render, redirect, HttpResponse
from .. import models, forms
import time, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.utils import IntegrityError
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Q


# -----------------------代偿列表-------------------------#
@login_required
def compensatory(request, *args, **kwargs):  # 代偿列表
    print(__file__, '---->def compensatory')
    dun_state_list = models.Compensatories.DUN_STATE_LIST
    compensatory_list = models.Compensatories.objects.filter(**kwargs)

    ####分页信息###
    paginator = Paginator(compensatory_list, 10)
    page = request.GET.get('page')
    try:
        compensatory_list = paginator.page(page)
    except PageNotAnInteger:
        compensatory_list = paginator.page(1)
    except EmptyPage:
        compensatory_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/dun/compensatory.html', locals())


@login_required
def compensatory_scan(request, compensatory_id):
    pass
