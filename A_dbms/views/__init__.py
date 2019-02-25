# ----------------------v_index首页管理视图--------------------#
from .v_index import index
# ----------------------v_article合项目管理视图--------------------#
from .v_article import (
    article, article_scan, article_scan_agree, article_scan_lending)
from .v_article_act import (
    article_add_ajax, article_feedback_ajax, article_edit_ajax, article_del_ajax)
# ----------------------v_meeting评审会视图--------------------#
from .v_meeting import (
    meeting, meeting_scan, meeting_notice, meeting_scan_article)
from .v_meeting_act import (
    meeting_article_del_ajax, meeting_article_add_ajax, meeting_edit_ajax,
    meeting_del_ajax, meeting_close_ajax, meeting_add_ajax, meeting_allot_add_ajax,
    meeting_allot_del_ajax)
# ----------------------v_appraisal评审视图--------------------#
from .v_appraisal import (appraisal, appraisal_scan, appraisal_scan_lending, summary_scan)
from .v_appraisal_act import (
    article_sign_ajax, guarantee_add_ajax, guarantee_del_ajax, single_del_ajax, comment_edit_ajax,
    single_quota_ajax, lending_del_ajax, lending_order_ajax, article_change_ajax)
# ----------------------v_agree合同管理视图--------------------#
from .v_agree import (agree, agree_scan, agree_preview)
from .v_agree_act import (agree_add_ajax, counter_add_ajax, agree_sign_ajax, counter_del_ajax)
# ----------------------v_warrant权证管理视图--------------------#
from .v_warrant import (
    warrant, warrant_scan, warrant_agree, warrant_agree_scan, warrant_agree_warrant, house, ground,
    soondue_draft, overdue_draft)
from .v_warrant_act import (
    warrant_add_ajax, warrant_del_ajax, warrant_edit_ajax, owership_add_ajax, owership_del_ajax,
    guaranty_add_ajax, guaranty_del_ajax, storages_add_ajax, housebag_add_ajax, draftextend_add_ajax,
    evaluate_add_ajax)

# ----------------------v_provide放款管理视图--------------------#
from .v_provide import (
    provide_agree, provide_agree_scan, provide_agree_notify, provide, provide_scan, overdue, soondue)
from .v_provide_act import (
    counter_sign_ajax, ascertain_add_ajax, notify_add_ajax, notify_del_ajax, provide_add_ajax,
    provide_del_ajax, repayment_add_ajax, repayment_del_ajax)

from .v_pigeonhole import pigeonhole, pigeonhole_scan, pigeonhole_add_ajax
# ----------------------v_review保后管理视图--------------------#
from .v_review import review, review_scan, review_plan_ajax, review_update_ajax
# ----------------------v_dun追偿视图--------------------#
from .v_dun import (compensatory, compensatory_scan, dun, dun_scan, seal, overdue_seal,soondue_seal,
                    compensatory_add_ajax)
from .v_dun_act import (clue_add_ajax, clue_del_ajax, sealup_add_ajax, standing_add_ajax,
                        standing_del_ajax, charge_add_ajax, charge_del_ajax, retrieve_add_ajax,
                        retrieve_del_ajax)

# ----------------------v_custom客户管理视图--------------------#
from .v_custom import (custom, custom_scan)
from .v_custom_act import (custom_add_ajax, custom_del_ajax, custom_edit_ajax, shareholder_add_ajax)
from .v_external import cooperative, soondue_cooperator, overdue_cooperator

# 部门、员工
from .v_interior import department, department_add, department_edit
from .v_interior import department_del
from .v_interior import employee, employee_add, employee_edit, employee_del
from .v_interior import employee_del_ajax
