# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
{
    "name": "Serbian Accounting Invoice extensions",
    "summary": "Invoice extensions for serbian COA",
    "version": "15.0.0.2.0",
    "license": "LGPL-3",
    "author": "Modoolar",
    "category": "Localization",
    "depends": ["l10n_rs"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_move_views.xml",
        "views/account_tax_views.xml",
        "views/vat_legislation_mention_views.xml",
        "views/report_invoice.xml",
        "views/menuitem.xml",
    ],
    "installable": True,
}
