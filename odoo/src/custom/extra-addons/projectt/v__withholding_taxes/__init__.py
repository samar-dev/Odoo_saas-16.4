from . import models, wizards
from odoo import registry
from odoo.tests.common import get_db_name


def post_load():
    dbname = get_db_name()
    with registry(dbname).cursor() as cr:
        # we don't need this view any more and a field has been deleted,
        # but it depends on how the module gets upĝraded so to avoid an internal server
        # we delete this view when we upgrade if we found it
        # this code will be deleted in the future
        cr.execute(
            "delete from ir_ui_view"
            " where arch_fs='v__withholding_taxes/views/core/account_journal.xml'"
        )
