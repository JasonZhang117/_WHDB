from django.shortcuts import render, redirect, HttpResponse
from .. import models, forms
import time, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.utils import IntegrityError
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Q


# -----------------------保后列表---------------------#
@login_required
def review(request):  # 保后列表
    print(__file__, '---->def review')
    custom_list = models.Customes.objects.filter(
        Q(custom_flow__gt=0) | Q(custom_accept__gt=0) | Q(custom_back__gt=0)).order_by('-credit_amount')

    ####分页信息###
    paginator = Paginator(custom_list, 10)
    page = request.GET.get('page')
    try:
        custom_list = paginator.page(page)
    except PageNotAnInteger:
        custom_list = paginator.page(1)
    except EmptyPage:
        custom_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/review/review.html', locals())
