from django.urls import path
from . import views

app_name = 'dbms'
urlpatterns = [
    # -----------------------主页管理-------------------------#
    path('', views.index, name='index'),  # /dbms/
    # path('', views.index, name='index'),  # /dbms/
    # -----------------------项目管理-------------------------#
    path('article/',
         views.article, name='article_all'),
    path('article/<int:article_state>/',
         views.article, name='article'),  # /dbms/article/(0-9)
    path('article/add/',
         views.article_add_ajax, name='article_add_ajax'),
    path('article/edit/',
         views.article_edit_ajax, name='article_edit_ajax'),
    path('article/feedback/',
         views.article_feedback_ajax, name='article_feedback_ajax'),
    path('article/del/',
         views.article_del_ajax, name='article_del_ajax'),
    # -----------------------项目管理-------------------------#
    path('article/scan/<int:article_id>/',
         views.article_scan, name='article_scan_all'),
    path('article/scan/<int:article_id>/<int:agree_id>',
         views.article_scan_agree,
         name='article_scan_agree'),
    # -----------------------评审会-------------------------#
    path('meeting/<int:meeting_state>',
         views.meeting, name='meeting'),
    path('meeting/',
         views.meeting, name='meeting_all'),

    path('meeting/add/',
         views.meeting_add_ajax, name='meeting_add_ajax'),
    path('meeting/allot/',
         views.meeting_allot_ajax, name='meeting_allot_ajax'),

    path('meeting/comment/',
         views.comment_edit_ajax, name='comment_edit_ajax'),

    path('meeting/single/',
         views.single_quota_ajax, name='single_quota_ajax'),
    path('meeting/single/del/',
         views.single_del_ajax, name='single_del_ajax'),
    path('meeting/article/sign/',
         views.article_sign_ajax, name='article_sign_ajax'),

    path('meeting/edit/',
         views.meeting_edit_ajax, name='meeting_edit_ajax'),
    path('meeting/close/',
         views.meeting_close_ajax, name='meeting_close_ajax'),
    path('meeting/del/',
         views.meeting_del_ajax, name='meeting_del_ajax'),
    path('meeting/article/add/',
         views.meeting_article_add_ajax, name='meeting_article_add_ajax'),
    path('meeting/article/del/',
         views.meeting_article_del_ajax, name='meeting_article_del_ajax'),

    path('meeting/scan/<int:meeting_id>/',
         views.meeting_scan, name='meeting_scan'),
    path('meeting/scan/<int:meeting_id>/<int:article_id>/',
         views.meeting_scan_article,
         name='meeting_scan_article'),
    # -----------------------评审管理-------------------------#

    path('appraisal/<int:article_state>',
         views.appraisal,
         name='appraisal'),
    path('appraisal/',
         views.appraisal,
         name='appraisal_all'),

    path('appraisal/edit/<int:id>/',
         views.appraisal_edit,
         name='appraisal_edit'),
    path('appraisal/del/<int:id>/',
         views.appraisal_del,
         name='appraisal_del'),
    path('appraisal/sign/<int:id>/',
         views.appraisal_sign,
         name='appraisal_sign'),
    # -----------------------合同管理-------------------------#
    path('agree/',
         views.agree, name='agree_all'),
    path('agree/<int:agree_state>/',
         views.agree, name='agree'),  # /dbms/article/(0-9)
    path('agree/add/',
         views.agree_add, name='agree_add'),
    path('agree/add-ajax/',
         views.agree_add_ajax, name='agree_add_ajax'),
    path('agree/edit/<int:id>/',
         views.agree_edit,
         name='agree_edit'),
    path('agree/scan/<int:agree_id>/',
         views.agree_scan,
         name='agree_scan'),
    path('agree/preview/<int:agree_id>/',
         views.agree_preview,
         name='agree_preview'),

    # path('agree/del/',
    #      views.agree_del,
    #      name='agree_del'),
    # -----------------------权证管理-------------------------#
    path('warrant/',
         views.warrant, name='warrant_all'),
    # -----------------------放款管理-------------------------#
    path('provide/', views.provide, name='provide'),
    # path('provide/add/',
    #      views.provide_add,
    #      name='provide_add'),
    path('provide/edit/<int:agree_id>/',
         views.provide_edit,
         name='provide_edit'),

    # -----------------------保后管理-------------------------#
    path('review/',
         views.review, name='review_all'),

    # 部门
    path('department/', views.department, name='department'),
    # path('department/', views.Departments.as_view),
    path('department/add/',
         views.department_add,
         name='department_add'),
    path('department/edit/<int:department_id>/',
         views.department_edit,
         name='department_edit'),
    path('department/del/<int:department_id>/',
         views.department_del,
         name='department_del'),

    # 员工
    path('employee/', views.employee, name='employee'),
    path('employee/add/',
         views.employee_add,
         name='employee_add'),
    # path('employee/add_ajax/',
    #      views.employee_add_ajax,
    #      name='employee_add_ajax'),
    path('employee/edit/<int:employee_id>/',
         views.employee_edit,
         name='employee_edit'),
    path('employee/del/<int:employee_id>/',
         views.employee_del,
         name='employee_del'),
    path('employee/del/ajax',
         views.employee_del_ajax,
         name='employee_del_ajax'),

    # 客户
    path('custome/', views.custome, name='custome'),
    path('custome/add/',
         views.custome_add,
         name='custome_add'),
    path('custome/edit/<int:custome_id>/',
         views.custome_edit,
         name='custome_edit'),
    path('custome/del/<int:custome_id>/',
         views.custome_del,
         name='custome_del'),

    # 房产

    # 行业
    path('industry/', views.industry, name='industry'),
    path('industry/add/',
         views.industry_add,
         name='industry_add'),
    path('industry/edit/<int:industry_id>/',
         views.industry_edit,
         name='industry_edit'),

    # 区域
    path('district/', views.district, name='district'),

]
