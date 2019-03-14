from django.urls import path
from . import views

app_name = 'dbms'
urlpatterns = [
    # -----------------------主页管理-------------------------#
    path('', views.index, name='index'),  # 菜单
    # -----------------------article项目管理-------------------------#
    path('article/', views.article, name='article_all'),  # 菜单-项目管理
    path('article/<int:article_state>/', views.article, name='article'),  # /dbms/article/(0-9)
    path('article/scan/<int:article_id>/', views.article_scan, name='article_scan'),
    path('article/agree/<int:article_id>/<int:agree_id>/', views.article_scan_agree, name='article_scan_agree'),
    path('article/lending/<int:article_id>/<int:lending_id>/', views.article_scan_lending, name='article_scan_lending'),

    path('article/add/', views.article_add_ajax, name='article_add_ajax'),
    path('article/del/', views.article_del_ajax, name='article_del_ajax'),
    path('article/edit/', views.article_edit_ajax, name='article_edit_ajax'),
    path('article/feedback/', views.article_feedback_ajax, name='article_feedback_ajax'),
    # -----------------------meeting评审会-------------------------#
    path('meeting/', views.meeting, name='meeting_all'),  # 菜单-评审管理-评审会
    path('meeting/<int:review_model>', views.meeting, name='meeting'),
    path('meeting/scan/<int:meeting_id>/', views.meeting_scan, name='meeting_scan'),
    path('meeting/scan/<int:meeting_id>/<int:article_id>/', views.meeting_scan_article, name='meeting_scan_article'),
    path('meeting/notice/<int:meeting_id>/', views.meeting_notice, name='meeting_notice'),
    path('meeting/experts/', views.experts, name='meeting_experts'),

    path('meeting/add/', views.meeting_add_ajax, name='meeting_add_ajax'),
    path('meeting/allot/add/', views.meeting_allot_add_ajax, name='meeting_allot_add_ajax'),
    path('meeting/allot/del/', views.meeting_allot_del_ajax, name='meeting_allot_del_ajax'),
    path('meeting/edit/', views.meeting_edit_ajax, name='meeting_edit_ajax'),
    path('meeting/close/', views.meeting_close_ajax, name='meeting_close_ajax'),
    path('meeting/del/', views.meeting_del_ajax, name='meeting_del_ajax'),
    path('meeting/article/add/', views.meeting_article_add_ajax, name='meeting_article_add_ajax'),
    path('meeting/article/del/', views.meeting_article_del_ajax, name='meeting_article_del_ajax'),
    # -----------------------appraisal评审管理-------------------------#
    path('appraisal/', views.appraisal, name='appraisal_all'),  # 菜单-评审管理-项目评审
    path('appraisal/<int:article_state>/', views.appraisal, name='appraisal'),  # /dbms/article/(0-9)
    path('appraisal/scan/<int:article_id>/', views.appraisal_scan, name='appraisal_scan'),
    path('appraisal/scan/<int:article_id>/<int:lending_id>/', views.appraisal_scan_lending,
         name='appraisal_scan_lending'),
    path('appraisal/summary/<int:article_id>/', views.summary_scan, name='appraisal_summary_scan'),

    path('appraisal/comment/', views.comment_edit_ajax, name='appraisal_comment_edit_ajax'),
    path('appraisal/single/add/', views.single_quota_ajax, name='appraisal_single_quota_ajax'),
    path('appraisal/single/del/', views.single_del_ajax, name='appraisal_single_del_ajax'),
    path('appraisal/lending/add/', views.lending_order_ajax, name='appraisal_lending_order_ajax'),
    path('appraisal/lending/del/', views.lending_del_ajax, name='appraisal_lending_del_ajax'),
    path('appraisal/sign/', views.article_sign_ajax, name='appraisal_article_sign_ajax'),
    path('appraisal/article/change/', views.article_change_ajax, name='appraisal_article_change_ajax'),
    path('appraisal/guarantee/add/', views.guarantee_add_ajax, name='appraisal_guarantee_add_ajax'),
    path('appraisal/guarantee/del/', views.guarantee_del_ajax, name='appraisal_guarantee_del_ajax'),
    # -----------------------agree合同管理-------------------------#
    path('agree/', views.agree, name='agree_all'),  # 菜单-合同管理
    path('agree/<int:agree_state>/', views.agree, name='agree'),  # /dbms/article/(0-9)
    path('agree/scan/<int:agree_id>/', views.agree_scan, name='agree_scan'),
    path('agree/preview/<int:agree_id>/', views.agree_preview, name='agree_preview'),

    path('agree/add/', views.agree_add_ajax, name='agree_add_ajax'),
    path('agree/sign/', views.agree_sign_ajax, name='agree_sign_ajax'),
    path('agree/counter/add/', views.counter_add_ajax, name='agree_counter_add_ajax'),
    path('agree/counter/del/', views.counter_del_ajax, name='agree_counter_del_ajax'),
    # -----------------------warrant权证管理-------------------------#
    path('warrant/', views.warrant, name='warrant_all'),  # 菜单-权证管理-所有权证
    path('warrant/<int:warrant_typ>/', views.warrant, name='warrant'),  # /dbms/warrant/(0-9)
    path('warrant/scan/<int:warrant_id>/', views.warrant_scan, name='warrant_scan'),
    path('warrant/agree/', views.warrant_agree, name='warrant_agree_all'),
    path('warrant/agree/<int:agree_state>', views.warrant_agree, name='warrant_agree'),
    path('warrant/agree/scan/<int:agree_id>/', views.warrant_agree_scan, name='warrant_agree_scan'),
    path('warrant/agree/warrant/<int:agree_id>/<int:warrant_id>/', views.warrant_agree_warrant,
         name='warrant_agree_warrant'),
    path('warrant/draft/soondue/', views.soondue_draft, name='warrant_soondue_draft_all'),  #
    path('warrant/draft/overdue/', views.overdue_draft, name='warrant_overdue_draft_all'),  #

    path('warrant/add/', views.warrant_add_ajax, name='warrant_add_ajax'),
    path('warrant/del/', views.warrant_del_ajax, name='warrant_del_ajax'),
    path('warrant/edit/', views.warrant_edit_ajax, name='warrant_edit_ajax'),
    path('warrant/owership/add/', views.owership_add_ajax, name='warrant_owership_add_ajax'),
    path('warrant/owership/del/', views.owership_del_ajax, name='warrant_owership_del_ajax'),
    path('warrant/housebag/add/', views.housebag_add_ajax, name='warrant_housebag_add_ajax'),
    path('warrant/draftbag/add/', views.draftextend_add_ajax, name='warrant_draftextend_add_ajax'),
    path('warrant/guaranty/add/', views.guaranty_add_ajax, name='warrant_guaranty_add_ajax'),
    path('warrant/guaranty/del/', views.guaranty_del_ajax, name='warrant_guaranty_del_ajax'),
    path('warrant/storages/add/', views.storages_add_ajax, name='warrant_storages_add_ajax'),
    path('warrant/evaluate/add/', views.evaluate_add_ajax, name='warrant_evaluate_add_ajax'),

    # -----------------------house房产管理-------------------------#
    path('house/', views.house, name='warrant_house_all'),  # 菜单-权证管理-房产列表
    path('house/<int:house_app>/', views.house, name='warrant_house'),  # /dbms/house/(0-9)
    # -----------------------ground土地管理-------------------------#
    path('ground/', views.ground, name='warrant_ground_all'),  # 菜单-权证管理-土地列表
    path('ground/<int:application>/', views.ground, name='warrant_ground'),  # /dbms/ground/(0-9)
    # -----------------------放款管理-------------------------#
    path('provide/agree/', views.provide_agree, name='provide_agree_all'),
    path('provide/agree/<int:agree_state>/', views.provide_agree, name='provide_agree'),  # /dbms/provide/(0-9)
    path('provide/agree/scan/<int:agree_id>/', views.provide_agree_scan, name='provide_agree_scan'),
    path('provide/agree/notify/<int:agree_id>/<int:notify_id>/', views.provide_agree_notify,
         name='provide_agree_notify'),
    path('provide/notify/', views.notify, name='provide_notify_all'),  #
    path('provide/notify/scan/<int:notify_id>/', views.notify_scan, name='provide_notify_scan'),
    path('provide/', views.provide, name='provide_all'),  # 菜单-放款管理-放款
    path('provide/<int:provide_status>/', views.provide, name='provide'),  # /dbms/grant/(0-9)
    path('provide/scan/<int:provide_id>/', views.provide_scan, name='provide_scan'),
    path('provide/overdue/', views.overdue, name='provide_overdue_all'),  # 菜单-放款管理-逾期项目
    path('provide/soondue/', views.soondue, name='provide_soondue_all'),  # 菜单-放款管理-即将到期

    path('provide/counter/sign/', views.counter_sign_ajax, name='provide_counter_sign_ajax'),
    path('provide/ascertain/add/', views.ascertain_add_ajax, name='provide_ascertain_add_ajax'),
    path('provide/notify/add/', views.notify_add_ajax, name='provide_notify_add_ajax'),
    path('provide/notify/del/', views.notify_del_ajax, name='provide_notify_del_ajax'),
    path('provide/add/', views.provide_add_ajax, name='provide_add_ajax'),
    path('provide/del/', views.provide_del_ajax, name='provide_del_ajax'),
    path('provide/repayment/add/', views.repayment_add_ajax, name='provide_repayment_add_ajax'),
    path('provide/repayment/del/', views.repayment_del_ajax, name='provide_repayment_del_ajax'),
    # -----------------------归档管理-------------------------#
    path('pigeonhole/', views.pigeonhole, name='pigeonhole_all'),  # 菜单-放款管理-放款
    path('pigeonhole/<int:implement>/', views.pigeonhole, name='pigeonhole'),  # /dbms/grant/(0-9)
    path('pigeonhole/scan/<int:provide_id>/', views.pigeonhole_scan, name='pigeonhole_scan'),
    path('pigeonhole/overdue/', views.pigeonhole_overdue, name='pigeonhole_overdue_all'),  # 菜单-放款管理-放款

    path('pigeonhole/add/', views.pigeonhole_add_ajax, name='pigeonhole_add_ajax'),
    # -----------------------保后管理-------------------------#
    path('review/', views.review, name='review_all'),  # 菜单-保后管理
    path('review/<int:review_state>/', views.review, name='review'),  # 菜单-保后管理
    path('review/scan/<int:custom_id>/', views.review_scan, name='review_scan'),  #
    path('review/overdue/', views.review_overdue, name='review_overdue_all'),  # 菜单-保后管理

    path('review/plan/', views.review_plan_ajax, name='review_plan_ajax'),  #
    path('review/update/', views.review_update_ajax, name='review_update_ajax'),  #
    # -----------------------代偿管理-------------------------#
    path('compensatory/', views.compensatory, name='compensatory_all'),  # 菜单-追偿管理
    path('compensatory/<int:dun_state>/', views.compensatory, name='compensatory'),
    path('compensatory/scan/<int:compensatory_id>/', views.compensatory_scan, name='compensatory_scan'),

    path('compensatory/add/', views.compensatory_add_ajax, name='compensatory_add_ajax'),
    # -----------------------追偿管理-------------------------#
    path('dun/', views.dun, name='dun_all'),  # 菜单-追偿管理
    path('dun/<int:dun_stage>/', views.dun, name='dun'),
    path('dun/scan/<int:dun_id>/', views.dun_scan, name='dun_scan'),
    path('dun/seal/', views.seal, name='dun_seal_all'),
    path('dun/seal/<int:seal_state>/', views.seal, name='dun_seal'),
    path('dun/seal/scan/<int:dun_id>/<int:warrant_id>/', views.seal_scan, name='dun_seal_scan'),
    path('dun/seal/overdue/', views.overdue_seal, name='dun_overdue_seal_all'),
    path('dun/seal/soondue/', views.soondue_seal, name='dun_soondue_seal_all'),
    path('dun/search/overdue/', views.overdue_search, name='dun_overdue_search_all'),
    path('dun/add/', views.dun_add_ajax, name='dun_add_ajax'),
    path('dun/clue/add/', views.clue_add_ajax, name='dun_clue_add_ajax'),
    path('dun/clue/del/', views.clue_del_ajax, name='dun_clue_del_ajax'),
    path('dun/defendant/add/', views.defendant_add_ajax, name='dun_defendant_add_ajax'),
    path('dun/defendant/del/', views.defendant_del_ajax, name='dun_defendant_del_ajax'),
    path('dun/stage/add/', views.stage_add_ajax, name='dun_stage_add_ajax'),
    path('dun/stage/del/', views.stage_del_ajax, name='dun_stage_del_ajax'),
    path('dun/judgment/add/', views.judgment_add_ajax, name='dun_judgment_add_ajax'),
    path('dun/judgment/del/', views.judgment_del_ajax, name='dun_judgment_del_ajax'),
    path('dun/agent/add/', views.agent_add_ajax, name='dun_agent_add_ajax'),
    path('dun/staff/add/', views.staff_add_ajax, name='dun_staff_add_ajax'),
    path('dun/sealup/add/', views.sealup_add_ajax, name='dun_sealup_add_ajax'),
    path('dun/inquiry/add/', views.inquiry_add_ajax, name='dun_inquiry_add_ajax'),
    path('dun/standing/add/', views.standing_add_ajax, name='dun_standing_add_ajax'),
    path('dun/standing/del/', views.standing_del_ajax, name='dun_standing_del_ajax'),
    path('dun/charge/add/', views.charge_add_ajax, name='dun_charge_add_ajax'),
    path('dun/charge/del/', views.charge_del_ajax, name='dun_charge_del_ajax'),
    path('dun/retrieve/add/', views.retrieve_add_ajax, name='dun_retrieve_add_ajax'),
    path('dun/retrieve/del/', views.retrieve_del_ajax, name='dun_retrieve_del_ajax'),
    # -----------------------客户管理-------------------------#

    path('custom/', views.custom, name='custom_all'),  # 菜单-客户管理
    path('custom/<int:genre>/', views.custom, name='custom'),  # /dbms/cstom/(0-9)
    path('custom/scan/<int:custom_id>/', views.custom_scan, name='custom_scan'),

    path('custom/add/', views.custom_add_ajax, name='custom_add_ajax'),
    path('custom/del/', views.custom_del_ajax, name='custom_del_ajax'),
    path('custom/edit/', views.custom_edit_ajax, name='custom_edit_ajax'),
    path('custom/shareholder/add/', views.shareholder_add_ajax, name='custom_shareholder_add_ajax'),
    path('custom/spouse/add/', views.spouse_add_ajax, name='custom_spouse_add_ajax'),

    # ------------------------------合作机构--------------------------------------#
    path('cooperative/', views.cooperative, name='cooperative_all'),  # 菜单-合作机构
    path('cooperative/<int:cooperator_type>/', views.cooperative, name='cooperative'),  # /dbms/cstom/(0-9)
    path('cooperative/scan/<int:cooperator_id>/', views.cooperative_scan, name='cooperative_scan'),
    path('cooperative/soondue/', views.soondue_cooperator, name='cooperative_soondue_all'),
    path('cooperative/overdue/', views.overdue_cooperator, name='cooperative_overdue_all'),
    path('cooperative/agreement/add/', views.agreement_add_ajax, name='cooperative_agreement_add_ajax'),
    path('branch/', views.branches, name='branch_all'),
    path('branch/<int:branch_state>/', views.branches, name='branch'),

    # 员工
    path('employee/', views.employee, name='employee'),
    path('employee/add/', views.employee_add, name='employee_add'),
    path('employee/edit/<int:employee_id>/', views.employee_edit, name='employee_edit'),
    path('employee/del/<int:employee_id>/', views.employee_del, name='employee_del'),
    path('employee/del/ajax', views.employee_del_ajax, name='employee_del_ajax'),
    # 部门
    path('department/', views.department, name='department'),
    path('department/add/', views.department_add, name='department_add'),
    path('department/edit/<int:department_id>/', views.department_edit, name='department_edit'),
    path('department/del/<int:department_id>/', views.department_del, name='department_del'),

    path('search/custom/', views.search_custom_ajax, name='search_custom_ajax'),
    path('search/warrant/', views.search_warrant_ajax, name='search_warrant_ajax'),
    path('search/guarantee/', views.guarantee_warrant_ajax, name='search_guarantee_ajax'),

]
