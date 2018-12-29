# ----------------------v_index首页管理视图--------------------#
from .v_index import index
# ----------------------v_article合项目管理视图--------------------#
from .v_article import (article, article_add_ajax, article_feedback_ajax,
                        article_scan, article_edit_ajax,article_scan_lending,
                        article_scan_agree, article_del_ajax)
# ----------------------v_appraisal评审视图--------------------#
from .v_meeting import (meeting, meeting_scan, meeting_notice,
                        meeting_article_del_ajax, meeting_article_add_ajax,
                        meeting_edit_ajax, meeting_del_ajax,
                        meeting_close_ajax, meeting_scan_article,
                        meeting_add_ajax, meeting_allot_ajax)

from .v_appraisal import (appraisal, appraisal_scan, appraisal_scan_lending,
                          article_sign_ajax, guarantee_add_ajax, guarantee_del_ajax,
                          single_del_ajax, comment_edit_ajax,
                          single_quota_ajax, lending_del_ajax, lending_order_ajax)

# ----------------------v_agree合同管理视图--------------------#
from .v_agree import (agree, agree_add_ajax, counter_add_ajax,
                      agree_scan, agree_preview)
# ----------------------v_warrant权证管理视图--------------------#
from .v_warrant import (warrant, house, ground, warrant_add_ajax,
                        warrant_del_ajax, warrant_edit_ajax, owership_add_ajax,
                        owership_del_ajax, guaranty_add_ajax, guaranty_del_ajax,
                        storages_add_ajax, warrant_scan)
# ----------------------v_provide放款管理视图--------------------#
from .v_provide import provide, provide_edit

# ----------------------v_review保后管理视图--------------------#
from .v_review import review

# 客户、行业、区域
from .v_custom import (custom, custom_scan, custom_add_ajax,
                       custom_del_ajax, custom_edit_ajax)
# 部门、员工
from .v_interior import department, department_add, department_edit
from .v_interior import department_del
from .v_interior import employee, employee_add, employee_edit, employee_del
from .v_interior import employee_del_ajax
