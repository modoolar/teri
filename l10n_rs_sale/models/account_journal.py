# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import fields, models


class AccountJournal(models.Model):

    _inherit = "account.journal"

    downpayment_sequence = fields.Boolean(
        string="Dedicated Down Payment Sequence",
        help="Check this box if you want to set different "
        "sequence on down payments made from this journal",
        default=False,
    )
