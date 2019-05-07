from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from A_dbms import models
import json, datetime, time, re
from django.urls import resolve, reverse
from django.db.models import Q, F
from django.db.models import Avg, Min, Sum, Max, Count
from django.db import transaction


class MenuHelper(object):
    def __init__(self, request):
        self.request = request  # 当前请求的request对象
        self.current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
        self.authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
        self.menu_leaf_list = request.session.get('menu_leaf_list')  # 获取在菜单中显示的权限
        self.menu_list = request.session.get('menu_list')  # 获取所有菜单

    def menu_data_list(self):
        menu_leaf_dict = {}  # 有菜单权限字典
        open_leaf_parent_id = None
        # 归并所有的叶子节点
        for item in self.menu_leaf_list:
            item = {
                'id': item['id'],
                'url': item['url'],
                'url_name': item['url_name'],
                'caption': item['name'],
                'parent_id': item['carte'],
                'child': [],
                'status': True,  # 是否显示
                'open': False,
            }  # 替换每个字典的键
            if item['parent_id'] in menu_leaf_dict:
                menu_leaf_dict[item['parent_id']].append(item)
            else:
                menu_leaf_dict[item['parent_id']] = [item, ]
            # if re.match(item['url'], current_url):
            if item['url_name'] == self.current_url_name:
                item['open'] = True
                open_leaf_parent_id = item['parent_id']
        # 获取所有菜单字典
        '''将列表menu_list转换为字典，'''
        menu_dict = {}  # 菜单字典
        for item in self.menu_list:  # carte_list为列表，其中的元素为字典，取出列表中的字典元素为item
            item['child'] = []  # 将carte_list里的每个字典添加一个child键，值设置为一个空列表
            menu_dict[item['id']] = item  # 将字典carte_dict键设为item字典的id值，值设为item字典
            item['status'] = False
            item['open'] = False
        # 将叶子节点添加到菜单中
        for k, v in menu_leaf_dict.items():
            menu_dict[k]['child'] = v  # 将权限挂到菜单上
            parent_id = k
            # 将后代中有叶子节点的菜单标记为【显示】
            while parent_id:
                menu_dict[parent_id]['status'] = True
                parent_id = menu_dict[parent_id]['parent_id']
        # 将已经选中的菜单标记为【展开】
        while open_leaf_parent_id:
            menu_dict[open_leaf_parent_id]['open'] = True
            open_leaf_parent_id = menu_dict[open_leaf_parent_id]['parent_id']

        menu_result = []
        for row in menu_dict.values():
            if not row['parent_id']:
                menu_result.append(row)
            else:
                menu_dict[row['parent_id']]['child'].append(row)
        return menu_result


def acc_login(request):
    ''':param request::return:'''
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    error_msg = ''
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('code')
        print("acc_login-->request.POST.get('username'):", username)
        print("acc_login-->request.POST.get('password'):", password)
        print("acc_login-->request.POST.get('code'):", code)
        user = authenticate(username=username, password=password)
        print('user:', user)
        if user:
            job_list_d = list(user.job.all().values('name'))  # 角色列表
            job_list = []
            for job in job_list_d:
                job_list.append(job["name"])
            request.session['job_list'] = job_list
            authority_list_d = list(models.Authorities.objects.filter(
                jobs__employees=user).distinct().values('url_name'))  # 权限列表
            authority_list = []
            for authority in authority_list_d:
                authority_list.append(authority["url_name"])
            request.session['authority_list'] = authority_list
            '''# 获取菜单的叶子节点，即：菜单的最后一层应该显示的权限'''
            menu_leaf_list = list(models.Authorities.objects.filter(
                jobs__employees=user).distinct().order_by('ordery').exclude(
                carte__isnull=True).values(
                'id', 'name', 'url', 'url_name', 'carte', 'ordery'))  # 有菜单权限列表
            request.session['menu_leaf_list'] = menu_leaf_list
            menu_list = list(models.Cartes.objects.filter(
                authority_carte__jobs__employees=user).distinct().order_by('ordery').values(
                'ordery', 'id', 'caption', 'parent_id'))  # # 获取所有的菜单列表
            request.session['menu_list'] = menu_list

            login(request, user)

            return redirect(request.GET.get('next', 'dbms:index'))
        else:
            error_msg = "用户名或密码错误！"

    return render(request, 'login.html', {'error_msg': error_msg})


def authority(func):
    def inner(request, *args, **kwargs):
        current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
        authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
        if not current_url_name in authority_list:
            response = {'status': True, 'message': None}
            response['status'] = False
            response['message'] = '无权限，请联系管理员！'
            result = json.dumps(response, ensure_ascii=False)
            return HttpResponse(result)
        return func(request, *args, **kwargs)

    return inner


def acc_logout(request):
    logout(request)
    return redirect('login')


@login_required
# @authority
def home(request):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    print('request.path_info', request.path_info)  # 当前url
    print('request.path:', request.path)
    print('resolve(request.path):', resolve(request.path))  # 路径转换为url_name等
    print('resolve(request.path):', resolve(request.path).url_name)  # 路径转换为url_name、app_name
    print('reverse(request.path):', reverse('home'))  # 将路径名转换为路径
    print('request.get_host:', request.get_host())
    print('request.GET.items():', request.GET.items())  # 获取get传递的参数对
    print('acc_login-->request.COOKIES:', request.COOKIES)
    print('acc_login-->request.session:', request.session)
    print('acc_login-->request.GET:', request.GET)
    print("request.session.get('authority_list'):", request.session.get('authority_list'))
    print("request.session.get('menu_leaf_list'):", request.session.get('menu_leaf_list'))

    # cooperator_list = models.Cooperators.objects.all()
    # for cooperator_obj in cooperator_list:
    #     cooperator_branch_flow_balance = models.Branches.objects.filter(
    #         cooperator=cooperator_obj).aggregate(
    #         Sum('branch_flow'))['branch_flow__sum']  # 授信银行项下，流贷余额
    #     if cooperator_branch_flow_balance:
    #         cooperator_list = models.Cooperators.objects.filter(id=cooperator_obj.id)
    #         cooperator_list.update(cooperator_flow=round(cooperator_branch_flow_balance, 2))
    #
    #     cooperator_branch_accept_balance = models.Branches.objects.filter(
    #         cooperator=cooperator_obj).aggregate(
    #         Sum('branch_accept'))['branch_accept__sum']  # 授信银行项下，流贷余额
    #     if cooperator_branch_accept_balance:
    #         cooperator_list = models.Cooperators.objects.filter(id=cooperator_obj.id)
    #         cooperator_list.update(cooperator_accept=round(cooperator_branch_accept_balance, 2))
    #
    #     cooperator_branch_back_balance = models.Branches.objects.filter(
    #         cooperator=cooperator_obj).aggregate(
    #         Sum('branch_back'))['branch_back__sum']  # 授信银行项下，流贷余额
    #     if cooperator_branch_back_balance:
    #         cooperator_list = models.Cooperators.objects.filter(id=cooperator_obj.id)
    #         cooperator_list.update(cooperator_back=round(cooperator_branch_back_balance, 2))

    # branch_list = models.Branches.objects.all()
    # for branch_obj in branch_list:
    #     '''PROVIDE_TYP_LIST = ((1, '流贷'), (11, '承兑'), (21, '保函'))'''
    #     branch_provide_1 = models.Provides.objects.filter(
    #         notify__agree__branch=branch_obj, provide_typ=1).aggregate(
    #         Sum('provide_balance'))['provide_balance__sum']  # 放款银行及放款品种项下，在保余额
    #     if branch_provide_1:
    #         branch_list = models.Branches.objects.filter(id=branch_obj.id)
    #         branch_list.update(branch_flow=branch_provide_1)
    #
    #     branch_provide_11 = models.Provides.objects.filter(
    #         notify__agree__branch=branch_obj, provide_typ=11).aggregate(
    #         Sum('provide_balance'))['provide_balance__sum']  # 放款银行及放款品种项下，在保余额
    #     if branch_provide_11:
    #         branch_list = models.Branches.objects.filter(id=branch_obj.id)
    #         branch_list.update(branch_accept=branch_provide_11)
    #
    #     branch_provide_21 = models.Provides.objects.filter(
    #         notify__agree__branch=branch_obj, provide_typ=21).aggregate(
    #         Sum('provide_balance'))['provide_balance__sum']  # 放款银行及放款品种项下，在保余额
    #     if branch_provide_21:
    #         branch_list = models.Branches.objects.filter(id=branch_obj.id)
    #         branch_list.update(branch_back=branch_provide_21)

    # agree_list = models.Agrees.objects.all()  # 合同
    # for agree_obj in agree_list:
    #     agree_provide_balance = models.Provides.objects.filter(
    #         notify__agree=agree_obj).aggregate(Sum('provide_balance'))['provide_balance__sum']  # 合同项下在保余额合计
    #     if agree_provide_balance:
    #         print('agree_provide_balance:', agree_provide_balance)
    #         agree_list_l = models.Agrees.objects.filter(id=agree_obj.id)
    #         agree_list_l.update(agree_balance=round(agree_provide_balance, 2))  # 合同，更新放款总额
    #     else:
    #         agree_list_l = models.Agrees.objects.filter(id=agree_obj.id)
    #         agree_list_l.update(agree_balance=0)  # 合同，更新放款总额

    # dun_list = models.Dun.objects.all()
    # for dun_obj in dun_list:
    #     dun_list_o = models.Dun.objects.filter(id=dun_obj.id)
    #     dun_balance = round(dun_obj.dun_amount - dun_obj.dun_retrieve_sun + dun_obj.dun_charge_sun, 2)
    #     dun_list_o.update(dun_balance=dun_balance)

    # seal_list = models.Seal.objects.filter(dun_id=6)
    # for seal_obj in seal_list:
    #     seal_list_l = models.Seal.objects.filter(id=seal_obj.id)
    #     seal_list_l.update(seal_state=21)
    #     sealup_list = models.Sealup.objects.filter(seal=seal_obj).update(sealup_type=21)

    # dun_list = models.Dun.objects.all()
    # for dun_obj in dun_list:
    #     for warrant_obj in dun_obj.warrant.all():
    #         seal_list = models.Seal.objects.filter(dun=dun_obj, warrant=warrant_obj)
    #         if not seal_list:
    #             models.Seal.objects.create(dun=dun_obj, warrant=warrant_obj, seal_state=1,
    #                                        sealor=request.user, )
    # article_list = models.Articles.objects.all()
    # for article_obj in article_list:
    #     for expert_obj in article_obj.expert.all():
    #         comment_list = models.Comments.objects.filter(summary=article_obj, expert=expert_obj)
    #         if not comment_list:
    #             models.Comments.objects.create(summary=article_obj, expert=expert_obj,
    #                                            comment_buildor=request.user)
    # aritcle_obj = models.Articles.objects.get(article_num='众诚瑞丰-201903-1')
    # article_comment_amount = aritcle_obj.comment_summary.exclude(comment_type=0).count()
    # print(aritcle_obj, article_comment_amount)

    # provide_accrual = models.Provides.objects.filter(
    #     provide_date__year=2018).aggregate(Sum('provide_money'))['provide_money__sum']  # 发生额

    # custom_list = models.Customes.objects.all()
    # for custom_obj in custom_list:
    #     custom_article = models.Articles.objects.filter(custom=custom_obj).order_by('-id').first()
    #     if custom_article:
    #         models.Customes.objects.filter(id=custom_obj.id).update(managementor=custom_article.director)

    # provide_list = models.Provides.objects.all().order_by('provide_date')
    # for provide_obj in provide_list:
    #     custom_list = models.Customes.objects.filter(
    #         article_custom__lending_summary__agree_lending__notify_agree__provide_notify=provide_obj)
    #     custom_list.update(lately_date=provide_obj.provide_date)

    # agree_list = models.Agrees.objects.all()
    # for agree_obj in agree_list:
    #     agree_typ = agree_obj.agree_typ
    #     agree_name = 0
    #     if agree_typ in [1, 41]:
    #         agree_name = 1
    #     elif agree_typ in [2, 42]:
    #         agree_name = 11
    #     elif agree_typ == 3:
    #         agree_name = 21
    #     elif agree_typ in [7, 47]:
    #         agree_name = 31
    #     agree_ll = models.Agrees.objects.filter(id=agree_obj.id).update(agree_name=agree_name)
    # agree_type = agree_obj.agree_typ
    # counter_list = agree_obj.counter_agree.all()
    # for counter_obj in counter_list:
    #     counter_typ = counter_obj.counter_typ
    #     counter_name = ''
    #     if agree_type in [1, 41]:
    #         if counter_typ == 1:
    #             counter_name = '保证反担保合同'
    #         elif counter_typ == 2:
    #             counter_name = '不可撤销的反担保函'
    #         elif counter_typ in [11, 12, 13, 14, 15]:
    #             counter_name = '抵押反担保合同'
    #         elif counter_typ == 31:
    #             counter_name = '应收账款质押反担保合同'
    #         elif counter_typ == 32:
    #             counter_name = '股权质押反担保合同'
    #         elif counter_typ in [33, 41]:
    #             counter_name = '权利质押反担保合同'
    #         elif counter_typ in [51, 52, 53]:
    #             counter_name = '预售合同'
    #     elif agree_type in [2, 42]:
    #         if counter_typ == 1:
    #             counter_name = '最高额保证反担保合同'
    #         elif counter_typ == 2:
    #             counter_name = '不可撤销的反担保函'
    #         elif counter_typ in [11, 12, 13, 14, 15]:
    #             counter_name = '最高额抵押反担保合同'
    #         elif counter_typ == 31:
    #             counter_name = '最高额应收账款质押反担保合同'
    #         elif counter_typ == 32:
    #             counter_name = '最高额股权质押反担保合同'
    #         elif counter_typ in [33, 41]:
    #             counter_name = '最高额权利质押反担保合同'
    #         elif counter_typ in [51, 52, 53]:
    #             counter_name = '预售合同'
    #     elif agree_type in [7, 47]:
    #         if counter_typ == 1:
    #             counter_name = '保证合同'
    #         elif counter_typ == 2:
    #             counter_name = '不可撤销的担保函'
    #         elif counter_typ in [11, 12, 13, 14, 15]:
    #             counter_name = '抵押合同'
    #         elif counter_typ == 31:
    #             counter_name = '应收账款质押合同'
    #         elif counter_typ == 32:
    #             counter_name = '股权质押合同'
    #         elif counter_typ in [33, 41]:
    #             counter_name = '权利质押合同'
    #         elif counter_typ in [51, 52, 53]:
    #             counter_name = '预售合同'
    #     counter_ll = models.Counters.objects.filter(id=counter_obj.id).update(counter_name=counter_name)

    # agree_list = models.Agrees.objects.all()
    # for agree_obj in agree_list:
    #     agree_type = agree_obj.agree_typ
    #     '''COUNTER_NAME_LIST = [(1, '保证反担保合同'), (2, '不可撤销的反担保函'),
    #                          (3, '抵押反担保合同'), (4, '应收账款质押反担保合同'),
    #                          (5, '股权质押反担保合同'), (6, '质押反担保合同'), (9, '预售合同'),
    #                          (21, '最高额保证反担保合同'),
    #                          (23, '最高额抵押反担保合同'), (24, '最高额应收账款质押反担保合同'),
    #                          (25, '最高额股权质押反担保合同'), (26, '最高额质押反担保合同'),
    #                          (41, '保证合同'),
    #                          (43, '抵押合同'), (44, '应收账款质押合同'),
    #                          (45, '股权质押合同'), (46, '质押合同')]'''
    #     counter_list = agree_obj.counter_agree.all()
    #     for counter_obj in counter_list:
    #         counter_typ = counter_obj.counter_typ
    #         counter_name = ''
    #         if agree_type in [1, 41]:
    #             if counter_typ == 1:
    #                 counter_name = 1
    #             elif counter_typ == 2:
    #                 counter_name = 2
    #             elif counter_typ in [11, 12, 13, 14, 15]:
    #                 counter_name = 3
    #             elif counter_typ == 31:
    #                 counter_name = 4
    #             elif counter_typ == 32:
    #                 counter_name = 5
    #             elif counter_typ in [33, 34, 39, 41]:
    #                 counter_name = 6
    #             elif counter_typ in [51, 52, 53]:
    #                 counter_name = 9
    #         elif agree_type in [2, 42]:
    #             if counter_typ == 1:
    #                 counter_name = 21
    #             elif counter_typ == 2:
    #                 counter_name = 2
    #             elif counter_typ in [11, 12, 13, 14, 15]:
    #                 counter_name = 23
    #             elif counter_typ == 31:
    #                 counter_name = 24
    #             elif counter_typ == 32:
    #                 counter_name = 25
    #             elif counter_typ in [33, 34, 39, 41]:
    #                 counter_name = 26
    #             elif counter_typ in [51, 52, 53]:
    #                 counter_name = 9
    #         elif agree_type in [7, 47]:
    #             if counter_typ == 1:
    #                 counter_name = 41
    #             elif counter_typ == 2:
    #                 counter_name = 2
    #             elif counter_typ in [11, 12, 13, 14, 15]:
    #                 counter_name = 43
    #             elif counter_typ == 31:
    #                 counter_name = 44
    #             elif counter_typ == 32:
    #                 counter_name = 45
    #             elif counter_typ in [33, 34, 39, 41]:
    #                 counter_name = 46
    #             elif counter_typ in [51, 52, 53]:
    #                 counter_name = 9
    #         counter_l = models.Counters.objects.filter(id=counter_obj.id)
    #         counter_l.update(counter_name=counter_name)

    # warrant_list = models.Warrants.objects.all()
    # for warrant in warrant_list:
    #     warrant_typ = warrant.warrant_typ
    #     evaluate_state = warrant.evaluate_state
    #     '''WARRANT_TYP_LIST = [
    #     (1, '房产'), (2, '房产包'), (5, '土地'), (6, '在建工程'), (11, '应收账款'),
    #     (21, '股权'), (31, '票据'), (41, '车辆'), (51, '动产'), (55, '其他'), (99, '他权')]'''
    #     # if warrant_typ in [6, 11, 21, 31, 41, 51, 55, 99]:
    #     #     '''EVALUATE_STATE_LIST = [(0, '待评估'), (11, '机构预估'), (21, '综合询价'), (31, '购买成本'),
    #     #                    (41, '拍卖评估'), (99, '无需评估')]'''
    #     #     models.Warrants.objects.filter(id=warrant.id).update(evaluate_state=99)
    #     if evaluate_state ==11:
    #         models.Warrants.objects.filter(id=warrant.id).update(evaluate_state=5)

    # article_list = models.Articles.objects.all().order_by('review_date')
    # for article in article_list:
    #     warrant_list = models.Warrants.objects.filter(
    #         lending_warrant__sure__lending__summary=article).update(
    #         meeting_date=article.review_date)
    # '''EVALUATE_STATE_LIST = [(0, '待评估'), (1, '机构评估'), (11, '机构预估'), (21, '综合询价'), (31, '购买成本'),
    #                        (41, '拍卖评估'), (99, '无需评估')]'''
    # '''ARTICLE_STATE_LIST = [(1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
    #                       (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销')]'''
    # warrant_list = models.Warrants.objects.exclude(
    #     Q(evaluate_state=99) | Q(evaluate_state=41)).order_by('evaluate_date')
    # '''EVALUATE_STATE_LIST = [(0, '待评估'), (5, '机构评估'), (11, '机构预估'), (21, '综合询价'), (31, '购买成本'),
    #                            (41, '拍卖评估'), (99, '无需评估')]'''
    # warrant_list = warrant_list.filter(lending_warrant__sure__lending__summary__article_state__in=[4, 5, 51, 52, 61])
    # ddd = []
    # for warrant in warrant_list:
    #     if warrant.evaluate_state == 0:
    #         ddd.append(warrant.id)
    #     else:
    #         cccc = warrant.meeting_date - warrant.evaluate_date
    #         if cccc.days > 365:
    #             ddd.append(warrant.id)
    # warrant_list = models.Warrants.objects.filter(id__in=ddd)
    # warrant_list = models.Warrants.objects.all()
    # for warrant in warrant_list:
    #     evaluate_state = warrant.evaluate_state
    #     if evaluate_state == 5:
    #         models.Warrants.objects.filter(id=warrant.id).update(evaluate_state=1)

    # singl_list = models.SingleQuota.objects.all()
    # for single in singl_list:
    #     f = single.rate
    #     models.SingleQuota.objects.filter(id=single.id).update(flow_rate=f)



    return render(request, 'test.html', locals())


def Caltime(date1, date2):
    # %Y-%m-%d为日期格式，其中的-可以用其他代替或者不写，但是要统一，同理后面的时分秒也一样；可以只计算日期，不计算时间。
    # date1=time.strptime(date1,"%Y-%m-%d %H:%M:%S")
    # date2=time.strptime(date2,"%Y-%m-%d %H:%M:%S")
    date1 = time.strptime(date1, "%Y-%m-%d")
    date2 = time.strptime(date2, "%Y-%m-%d")
    # 根据上面需要计算日期还是日期时间，来确定需要几个数组段。下标0表示年，小标1表示月，依次类推...
    # date1=datetime.datetime(date1[0],date1[1],date1[2],date1[3],date1[4],date1[5])
    # date2=datetime.datetime(date2[0],date2[1],date2[2],date2[3],date2[4],date2[5])
    date1 = datetime.datetime(date1[0], date1[1], date1[2])
    date2 = datetime.datetime(date2[0], date2[1], date2[2])
    # 返回两个变量相差的值，就是相差天数
    return date2 - date1
