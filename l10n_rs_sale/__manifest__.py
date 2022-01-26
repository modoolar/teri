# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
{
    "name": "Serbian Accounting Sale extensions",
    "summary": "Sale extensions for serbian COA",
    "version": "15.0.0.3.0",
    "license": "LGPL-3",
    "author": "Modoolar",
    "category": "Localization",
    "depends": ["l10n_rs", "sale"],
    "auto_install": True,
    "data": [
        "data/product_data.xml",
        "data/down_payment_data.xml",
        "views/account_journal_views.xml",
        "views/sale_order_views.xml",
        "views/report_invoice.xml",
        "views/report_sale_order.xml",
    ],
    "installable": True,
}
