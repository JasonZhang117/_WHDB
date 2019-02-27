from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from A_dbms import models
import datetime, time


def acc_login(request):
    ''':param request::return:'''
    print(__file__, '-->acc_login')
    print('acc_login-->request.COOKIES:', request.COOKIES)
    print('acc_login-->request.session:', request.session)
    print('acc_login-->request.GET:', request.GET)
    error_msg = ''
    if request.method == "POST":
        print('request.POST.get:', request.POST.get)
        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('code')
        print("acc_login-->request.POST.get('username'):", username)
        print("acc_login-->request.POST.get('password'):", password)
        print("acc_login-->request.POST.get('code'):", code)
        user = authenticate(username=username, password=password)
        if user:
            '''查询菜单并写入session'''
            menu_list = models.Menus.objects.filter(jobs__employees=user).distinct().order_by(
                'ordery').values('name', 'url_name')
            request.session['menus'] = list(menu_list)
            '''查询权限并写入session'''
            authority_list = models.Authorities.objects.filter(
                jobs__employees=user).distinct().values('name', 'url_name', 'carte')  # 权限列表
            request.session['authoritis'] = list(authority_list)
            '''查询菜单本写入session'''
            carte_list = models.Cartes.objects.filter(
                authority_carte__jobs__employees=user).distinct().values('name', 'ordery', 'parrent')  # 菜单列表

            request.session['cartes'] = list(carte_list)
            '''查询角色并写入session'''
            job_list = models.Jobs.objects.filter(employees=user).values('name')  # 角色列表
            request.session['jobs'] = list(job_list)

            # request.session['menus'] = [{'menu': '评审管理', 'url': 'dbms:article_all'},
            #                             {'menu': '个人主页', 'url': 'dbms:agree'}]
            login(request, user)
            return redirect(request.GET.get('next', 'dbms:index'))
        else:
            error_msg = "用户名或密码错误！"
    return render(request, 'login.html', {'error_msg': error_msg})


def acc_logout(request):
    logout(request)
    return redirect('login')


@login_required
def home(request):
    print(__file__, '---->def home')
    print("acc_login-->request.user:", request.user)
    carte_list = models.Cartes.objects.filter(
        authority_carte__jobs__employees=request.user).distinct().values(
        'id', 'parrent', 'name', 'ordery')  # 菜单列表
    print('carte_list:', carte_list)
    authority_list = models.Authorities.objects.filter(
        jobs__employees=request.user).distinct().values('name', 'url_name', 'carte')  # 权限列表

    no_carte_list = models.Authorities.objects.filter(
        jobs__employees=request.user).distinct().filter(
        carte__isnull=True).values('name', 'url_name', 'carte')  # 无菜单权限列表

    yes_carte_list = models.Authorities.objects.filter(
        jobs__employees=request.user).distinct().exclude(
        carte__isnull=True).values('id', 'name', 'url_name', 'carte')  # 有菜单权限列表

    yes_carte_dict = {}  # 有菜单权限字典
    for item in yes_carte_list:
        item = {
            'id': item['id'],
            'url': item['url_name'],
            'name': item['name'],
            'parrent': item['carte'],
            'child': []
        }  # 替换每个字典的键
        if item['parrent'] in yes_carte_dict:
            yes_carte_dict[item['parrent']].append(item)
        else:
            yes_carte_dict[item['parrent']] = [item, ]
    print('carte_list:', carte_list)

    carte_dict = {}  # 菜单字典
    '''将列表carte_list转换为字典，'''
    for item in carte_list:  # carte_list为列表，其中的元素为字典，取出列表中的字典元素为item
        item['child'] = []  # 将每个字典添加一个child键，值设置为一个空列表
        carte_dict[item['id']] = item  # 将字典carte_dict键设为item字典的id值，值设为item字典
    print(carte_dict)
    for k, v in yes_carte_dict.items():
        carte_dict[k]['child'] = v  # 将权限挂到菜单上
    print('carte_list:', carte_list)

    ''' [
            {'name': '项目管理', 'parrent': None, 'ordery': 1, 'chaild':[
                {'name': '评审管理', 'url': 'dbms/meeting/scan'},
                {'name': '评审管理', 'url': 'dbms/meeting/scan'},]},
            {'name': '评审管理', 'parrent': None, 'ordery': 2}
     ]'''
    result = []
    for row in carte_dict.values():
        if not row['parrent']:
            result.append(row)
        else:
            carte_dict[row['parrent']]['child'].append(row)
    print('carte_list:', carte_list)

    for item in result:
        print(item['name'])
        for r in item['child']:
            print('----', r['name'])
            for n in r['child']:
                print('-------->', n['name'])

    agree_list = models.Provides.objects.all()
    for agree in agree_list:
        agree_list_obj = models.Provides.objects.filter(id=agree.id)
    agree_obj = agree_list_obj.first()
    agree_amount = agree_obj.implement
    # return render(request, 'index.html', locals())

    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放完'), (61, '待变更'), (99, '已注销'))'''
    no_feedback_count = models.Articles.objects.filter(article_state=1).count()  # 待反馈
    '''IMPLEMENT_LIST = [(1, '未归档'), (11, '退回'), (21, '暂存风控'), (31, '移交行政'), (41, '已归档')]'''
    no_pigeonhole_count = models.Provides.objects.filter(implement__in=[1, 11]).count()  # 未归档
    '''AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '作废'))'''
    no_ascertain_count = models.Agrees.objects.filter(agree_state=31).count()  # 未落实

    today_str = time.strftime("%Y-%m-%d", time.gmtime())  # 元祖>>>字符窜
    print('time.strftime("%Y-%m-%d", time.gmtime()):', today_str)
    today_str = datetime.datetime.now().strftime('%Y-%m-%d')
    print("datetime.datetime.now().strftime('%Y-%m-%d'):", today_str)
    today_str = datetime.date.today()
    print('datetime.date.today():', today_str)

    date_th_later = datetime.datetime.now() - datetime.timedelta(days=-30)  # 30天前的日期
    print("date_th_later.strftime('%Y-%m-%d'):", date_th_later.strftime('%Y-%m-%d'))
    date_th_later = datetime.date.today() - datetime.timedelta(days=-30)  # 30天前的日期
    print('date_th_later:', date_th_later)
    print("date_th_later.strftime('%Y-%m-%d'):", date_th_later.strftime('%Y-%m-%d'))
    '''PROVIDE_STATUS_LIST = [(1, '在保'), (11, '解保'), (21, '代偿')]'''
    overdue_count = models.Provides.objects.filter(
        provide_status=1, due_date__lt=datetime.date.today()).count()  # 逾期
    soondue_count = models.Provides.objects.filter(
        provide_status=1, due_date__gte=datetime.date.today(), due_date__lt=date_th_later).count()  # 30天内到期
    '''DRAFT_STATE_LIST = (
        (1, '未入库'), (2, '已入库'), (21, '置换出库'), (31, '解保出库'), (41, '托收出库'), (99, '已注销'))'''
    soondue_draft_count = models.DraftExtend.objects.filter(
        draft_state__in=[1, 2], due_date__gte=datetime.date.today(), due_date__lt=date_th_later).count()  # 30天内到期
    overdue_draft_count = models.DraftExtend.objects.filter(
        draft_state__in=[1, 2], due_date__lt=datetime.date.today()).count()  # 逾期票据
    '''COOPERATOR_STATE_LIST = ((1, '正常'), (11, '注销'))'''
    soondue_cooperator_count = models.Cooperators.objects.filter(
        cooperator_state=1, due_date__gte=datetime.date.today(),
        due_date__lt=date_th_later).count()  # 30天内到期协议
    overdue_cooperator_count = models.Cooperators.objects.filter(
        cooperator_state=1, due_date__lt=datetime.date.today()).count()  # 逾期协议
    '''SEAL_STATE_LIST = ((1, '诉前保全'), (5, '首次首封'), (11, '首次轮封'), (21, '续查封'),
                       (51, '解除查封'), (99, '注销'))'''
    soondue_seal_count = models.Seal.objects.filter(
        seal_state__in=[1, 5, 11, 21], due_date__gte=datetime.date.today(),
        due_date__lt=date_th_later).count()  # 30天内到期协议
    overdue_seal_count = models.Seal.objects.filter(
        seal_state__in=[1, 5, 11, 21], due_date__lt=datetime.date.today()).count()  # 逾期协议

    return render(request, 'dbms/index_dbms.html', locals())
