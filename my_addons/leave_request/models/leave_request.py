from odoo import models, fields, api
from lxml import etree
import xml.etree.ElementTree as ET

from odoo.exceptions import AccessError


class LeaveRequest(models.Model):

    _name = 'leave.request'
    _description = "请假申请与审批"

    sn = fields.Char(string="请假申请单号", readonly=True)
    name = fields.Char(string="请假人", required=True, readonly=True)
    days = fields.Integer(string="请假天数", readonly=True)
    start_date = fields.Date(string="开始日期")
    end_date = fields.Date(string="结束日期")
    reason = fields.Text(string="请假事由")
    result = fields.Selection([('Yes', '同意'), ('No', '不同意')],
                              string='审批意见')
    approval_status = fields.Selection([('draft', '待提交'),
                                        ('pending', '待审批'), ('approved', '已审批')],
                                       string='审批状态', default='draft', readonly=True)
    last_seen = fields.Datetime("Last Seen", default=fields.Datetime.now)
    # 是否是通过提交按钮保存
    saved_via_submit_button = fields.Boolean(default=False)


    # @api.model
    # def get_user_group_name(self):
    #     print('打印信息')
    #     if self.env.user.has_group('leave_request.group_base'):
    #         return True
    #     else:
    #         return False
    #
    result_readonly = fields.Boolean(compute='_compute_result_readonly')
    field_readonly = fields.Boolean(compute='_compute_field_readonly')
    button_invisible = fields.Boolean(compute='_compute_submit_invisible')  # 审批同意拒绝按钮

    @api.model
    def create(self, vals):
        # 通过序列代码获取下一个序列号
        vals['sn'] = self.env['ir.sequence'].next_by_code('leave_request.sequence')
        return super(LeaveRequest, self).create(vals)

    # 审批意见权限控制
    # @api.depends('result')
    # def _compute_result_readonly(self):
    #     for record in self:
    #         # 检查当前用户是否属于 leave_request.group_base 组
    #         record.result_readonly = self.env.user.has_group('leave_request.group_manager')
    #         record.result_readonly = not record.result_readonly

    # 请假信息字段权限控制
    @api.depends('result')
    def _compute_field_readonly(self):
        for record in self:
            value = False
            if self.name == self.env.user.name and self.approval_status == "draft":
                value = False
            else:
                value = True
            record.field_readonly = value

    # 默认用户名称
    @api.model
    def default_get(self, fields_list):
        defaults = super(LeaveRequest, self).default_get(fields_list)
        defaults['name'] = self.env.user.name
        return defaults

    # 提交按钮保存
    def action_submit_leave(self):
        values = {
            'saved_via_submit_button': True,
            'approval_status': 'pending',
        }
        self.write(values)
        return True

    # 同意按钮保存
    def action_submit_agree(self):
        values = {
            'approval_status': 'approved',
            'result': 'Yes',
        }
        self.write(values)
        return True

    # 拒绝按钮保存
    def action_submit_refuse(self):
        values = {
            'approval_status': 'approved',
            'result': 'No',
        }
        self.write(values)
        return True

    # 同意拒绝按钮显示状态
    @api.depends('result')
    def _compute_submit_invisible(self):
        for record in self:
            if self.env.user.has_group('leave_request.group_manager') and self.approval_status == "pending":
                record.button_invisible = False
            else:
                record.button_invisible = True

    # 日期控制
    @api.constrains('start_date', 'end_date')
    def _check_date_order(self):
        for record in self:
            if record.start_date and record.end_date and record.end_date < record.start_date:
                raise models.ValidationError("结束日期必须大于开始日期")

    # 天数控制
    @api.onchange('start_date', 'end_date')
    def _compute_days(self):
        for record in self:
            if record.start_date and record.end_date:
                diff = record.end_date - record.start_date
                record.days = (diff.days + 1) if diff.days >= 0 else 1
            else:
                record.days = 0

    def return_to_parent(self):
        return {
            'type': 'ir.actions.act_window_close',
            'res_id': self.env.context.get('active_id', False),  # 获取当前记录id，如果不存在则关闭当前页面
        }

