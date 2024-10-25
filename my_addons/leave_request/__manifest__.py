# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': '请假申请与审批',
    'version': '1.0',
    'summary': '请假申请与审批',
    'sequence': 10,
    'description': """
    real estate
    """,
    'depends':[],
    'data': [
        'security/ir.model.access.csv',
        'security/leave_request_security.xml',
        'views/leave_request_views.xml',
    ],
    'application': True,

}
