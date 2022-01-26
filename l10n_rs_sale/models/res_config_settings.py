# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    deposit_default_journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Deposit Journal",
        domain="[('type', '=', 'sale')]",
        config_parameter="l10n_rs.default_deposit_journal_id",
        help="Default account journal used for payment advances",
    )
