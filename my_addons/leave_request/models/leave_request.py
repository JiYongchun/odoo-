from odoo import models, fields, api
from lxml import etree
import xml.etree.ElementTree as ET

from odoo.exceptions import AccessError


class LeaveRequest(models.Model):

    _name = 'leave.request'
    _description = "请假申请与审批"

    name = fields.Char(string="请假人", required=True, readonly=True)
    days = fields.Integer(string="请假天数")
    start_date = fields.Date(string="开始日期")
    end_date = fields.Date(string="结束日期")
    reason = fields.Text(string="请假事由")
    result = fields.Selection([('Yes', '同意'), ('No', '不同意')],
                              string='审批意见')
    last_seen = fields.Datetime("Last Seen", default=fields.Datetime.now)

    # @api.model
    # def get_user_group_name(self):
    #     print('打印信息')
    #     if self.env.user.has_group('leave_request.group_base'):
    #         return True
    #     else:
    #         return False
    #
    result_readonly = fields.Boolean(compute='_compute_result_readonly')

    @api.depends('result')
    def _compute_result_readonly(self):
        for record in self:
            # 检查当前用户是否属于 leave_request.group_base 组
            record.result_readonly = self.env.user.has_group('leave_request.group_base')

    # 默认用户名称
    @api.model
    def default_get(self, fields_list):
        defaults = super(LeaveRequest, self).default_get(fields_list)
        defaults['name'] = self.env.user.name
        return defaults


