##############################################################################
#
# Copyright (c) 2021 Modoolar (http://modoolar.com) All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contact support@modoolar.com
#
##############################################################################
{
    "name": "Serbian Accounting Reports",
    "summary": "Reports for serbian COA",
    "version": "15.0.0.1.0",
    "license": "LGPL-3",
    "author": "Modoolar",
    "category": "Localization",
    "depends": ["l10n_rs", "account_reports"],
    "data": [
        "security/ir.model.access.csv",
        "data/balance_sheet.xml",
        "data/profit_and_loss.xml",
        "data/tax_report.xml",
        "wizard/account_report_print_tax_l10n_rs_views.xml",
        "views/l10n_rs_reports.xml",
        "report/l10n_rs_report_template.xml",
        "report/l10n_rs_reports.xml",
    ],
    "installable": True,
}
