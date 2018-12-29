from django.urls import path
from . import views

app_name = 'dbms'
urlpatterns = [
    # -----------------------主页管理-------------------------#
    path('', views.index, name='index'),  # /dbms/
    # path('', views.index, name='index'),  # /dbms/
    # -----------------------article项目管理-------------------------#
    path('article/',
         views.article, name='article_all'),
    path('article/<int:article_state>/',
         views.article, name='article'),  # /dbms/article/(0-9)
    path('article/scan/<int:article_id>/',
         views.article_scan, name='article_scan_all'),
    path('article/scan/<int:article_id>/<int:lending_id>/',
         views.article_scan_lending, name='article_scan_lending'),

    path('article/add/', views.article_add_ajax),
    path('article/del/', views.article_del_ajax),
    path('article/edit/', views.article_edit_ajax),
    path('article/feedback/', views.article_feedback_ajax),

    # -----------------------meeting评审会-------------------------#
    path('meeting/<int:meeting_state>',
         views.meeting, name='meeting'),
    path('meeting/',
         views.meeting, name='meeting_all'),
    path('meeting/scan/<int:meeting_id>/',
         views.meeting_scan, name='meeting_scan'),
    path('meeting/scan/<int:meeting_id>/<int:article_id>/',
         views.meeting_scan_article, name='meeting_scan_article'),
    path('meeting/notice/<int:meeting_id>/',
         views.meeting_notice, name='meeting_notice'),

    path('meeting/add/', views.meeting_add_ajax),
    path('meeting/allot/', views.meeting_allot_ajax),
    path('meeting/edit/', views.meeting_edit_ajax),
    path('meeting/close/', views.meeting_close_ajax),
    path('meeting/del/', views.meeting_del_ajax),
    path('meeting/article/add/', views.meeting_article_add_ajax),
    path('meeting/article/del/', views.meeting_article_del_ajax),

    # -----------------------appraisal评审管理-------------------------#
    path('appraisal/',
         views.appraisal, name='appraisal'),
    path('appraisal/scan/<int:article_id>/',
         views.appraisal_scan, name='appraisal_scan'),
    path('appraisal/scan/<int:article_id>/<int:lending_id>/',
         views.appraisal_scan_lending, name='appraisal_scan_lending'),
    path('appraisal/comment/', views.comment_edit_ajax),
    path('appraisal/single/add/', views.single_quota_ajax),
    path('appraisal/single/del/', views.single_del_ajax),
    path('appraisal/lending/add/', views.lending_order_ajax),
    path('appraisal/lending/del/', views.lending_del_ajax),
    path('appraisal/sign/', views.article_sign_ajax),
    path('appraisal/guarantee/add/', views.guarantee_add_ajax),
    path('appraisal/guarantee/del/', views.guarantee_del_ajax),

    # -----------------------agree合同管理-------------------------#
    path('agree/',
         views.agree, name='agree_all'),
    path('agree/<int:agree_state>/',
         views.agree, name='agree'),  # /dbms/article/(0-9)
    path('agree/scan/<int:agree_id>/',
         views.agree_scan, name='agree_scan'),
    path('agree/preview/<int:agree_id>/',
         views.agree_preview, name='agree_preview'),

    path('agree/add/', views.agree_add_ajax),
    path('counter/add/', views.counter_add_ajax),

    # -----------------------warrant权证管理-------------------------#
    path('warrant/',
         views.warrant, name='warrant_all'),
    path('warrant/<int:warrant_typ>/',
         views.warrant, name='warrant'),  # /dbms/warrant/(0-9)
    path('warrant/scan/<int:warrant_id>/',
         views.warrant_scan, name='warrant_scan'),

    path('warrant/add/', views.warrant_add_ajax),
    path('warrant/del/', views.warrant_del_ajax),
    path('warrant/edit/', views.warrant_edit_ajax),
    path('warrant/owership/add/', views.owership_add_ajax),
    path('warrant/owership/del/', views.owership_del_ajax),
    path('warrant/guaranty/add/', views.guaranty_add_ajax),
    path('warrant/guaranty/del/', views.guaranty_del_ajax),
    path('warrant/storages/add/', views.storages_add_ajax),

    # -----------------------house房产管理-------------------------#
    path('house/',
         views.house, name='house_all'),
    path('house/<int:house_app>/',
         views.house, name='house'),  # /dbms/house/(0-9)

    # -----------------------ground土地管理-------------------------#
    path('ground/',
         views.ground, name='ground_all'),
    path('ground/<int:application>/',
         views.ground, name='ground'),  # /dbms/ground/(0-9)
    # -----------------------放款管理-------------------------#
    path('provide/', views.provide, name='provide_all'),
    path('provide/edit/<int:agree_id>/',
         views.provide_edit, name='provide_edit'),

    # -----------------------保后管理-------------------------#
    path('review/',
         views.review, name='review_all'),

    # -----------------------客户管理-------------------------#
    path('custom/',
         views.custom, name='custom_all'),
    path('custom/<int:genre>/',
         views.custom, name='custom'),  # /dbms/warrant/(0-9)
    path('custom/scan/<int:custom_id>/',
         views.custom_scan, name='custom_scan'),

    path('custom/add/', views.custom_add_ajax),
    path('custom/del/', views.custom_del_ajax),
    path('custom/edit/', views.custom_edit_ajax),

    # 员工
    path('employee/', views.employee, name='employee'),
    path('employee/add/',
         views.employee_add, name='employee_add'),
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

]
