# -*- coding: utf-8 -*-

from odoo import api, models
from lxml import etree
import ast
from odoo.http import request


class BaseModel(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def get_views(self, views, options=None):
        """If any button is invisible inside """
        view_ref = super(BaseModel, self).get_views(views, options)
        lst = [int(x) for x in request.httprequest.cookies.get('cids').split(',')]
        if view_ref.get('views'):
            actions_and_reports = []
            hidden_obj = self.env['model.access'].sudo().search(
                [('access_user_manager_id', 'in', self.env.user.access_user_manager_id.ids),
                 ('access_model_id.model', '=', self._name),
                 ('access_user_manager_id.access_company_ids', 'in', lst)])
            for access in hidden_obj:
                actions_and_reports += access.mapped('access_report_action_ids.access_action_id').ids
                actions_and_reports += access.mapped('access_server_action_ids.access_action_id').ids
            if hidden_obj:
                for view in ['form', 'list']:
                    view_obj = view_ref['views'].get(view)
                    if view_obj:
                        toolbar_obj = view_obj.get('toolbar')
                        print_obj = toolbar_obj.get('print')
                        action_obj = toolbar_obj.get('action')
                        for_print, for_action = [], []
                        if toolbar_obj and print_obj:
                            for print in print_obj:
                                if print['id'] in actions_and_reports:
                                    for_print.append(print)
                        if toolbar_obj and action_obj:
                            for action in action_obj:
                                if action['id'] in actions_and_reports:
                                    for_action.append(action)
                        [action_obj.remove(obj) for obj in for_action]
                        [print_obj.remove(obj) for obj in for_print]
        return view_ref

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        view_ref = super().get_view(view_id, view_type, **options)
        doc = etree.XML(view_ref['arch'])

        # Hide Buttons
        self.access_hide_button(doc, view_ref)

        # Field Access
        self.access_hide_field(doc, view_ref)
        lst = [int(x) for x in request.httprequest.cookies.get('cids').split(',')]
        # Hide Export All
        if view_type == 'tree':
            is_export_hide = self.env['model.access'].sudo().search(
                [('access_model_id.model', '=', view_ref['model']), ('access_user_manager_id.active', '=', True),
                 ('access_user_manager_id.access_company_ids', 'in', lst),
                 ('access_user_manager_id.access_user_ids', 'in', self.env.user.id), ('access_hide_export', '=', True)], limit=1)
            if is_export_hide:
                for ele in doc.xpath('//tree'):
                    ele.set('export_xlsx', '0')
        # Hide Page
        if view_type == 'form':
            self.access_hide_page(doc)
        # Hide Filter / GroupBy
        if view_type == 'search':
            doc = self.access_hide_filter_groupby(doc)
        view_ref['arch'] = etree.tostring(doc, encoding='unicode')
        if view_type == 'form':
            # remove external link
            hide_field_access = self.env['field.access'].sudo().search([
                ('access_user_manager_id.access_user_ids', 'in', self.env.user.id),
                ('access_user_manager_id.active', '=', True),
                ('access_model_id.model', '=', view_ref['model']), ('access_field_external_link', '=', True),
                ('access_user_manager_id.access_company_ids', 'in', lst)])
            if hide_field_access:
                for field in hide_field_access.mapped('access_field_id'):
                    if field.ttype in ['many2many', 'many2one']:
                        for field_ele in doc.xpath("//field[@name='" + field.name + "']"):
                            options = 'options' in field_ele.attrib.keys() and field_ele.attrib['options'] or "{}"
                            options = ast.literal_eval(options)
                            options.update({'no_create': True, 'no_create_edit': True, 'no_open': True})
                            field_ele.attrib.update({'options': str(options)})
                view_ref['arch'] = etree.tostring(doc, encoding='unicode')

            # Hide All Chatter
            if self.env['user.management'].sudo().search(
                    [('active', '=', True), ('access_user_ids', 'in', self.env.user.id),
                     ('access_company_ids', 'in', lst), ('access_hide_chatter', '=', True)], limit=1).id:
                for div in doc.xpath("//div[@class='oe_chatter']"):
                    div.getparent().remove(div)
                view_ref['arch'] = etree.tostring(doc, encoding='unicode')
        if view_type == 'kanban':
            hide_button_ids = self.env['button.tab.access'].sudo().search([
                ('access_model_id.model', '=', view_ref['model']), ('access_user_manager_id.active', '=', True),
                ('access_user_manager_id.access_user_ids', 'in', self._uid),
                ('access_user_manager_id.access_company_ids', 'in', lst)])
            for button in hide_button_ids:
                for btn in button.access_hide_button_ids:
                    element = doc.xpath(f"//a[@name='{btn.access_name}']")
                    for ele in element:
                        # if not ele.text.startswith('\n'):
                        ele.attrib.update({'class': 'd-none'})
                    element = doc.xpath(f"//button[@name='{btn.access_name}']")
                    for ele in element:
                        # if not ele.text.startswith('\n'):
                        ele.attrib.update({'class': 'd-none'})
                    element = doc.xpath(f"//object[@name='{btn.access_name}']")
                    for ele in element:
                        # if not ele.text.startswith('\n'):
                        ele.attrib.update({'class': 'd-none'})
                for link in button.access_kanban_button_ids:
                    if link.access_button_type == 'edit':
                        element = doc.xpath("//a[@type='edit']")
                    elif link.access_button_type == 'set_cover':
                        element = doc.xpath("//a[@type='set_cover']")
                    else:
                        element = doc.xpath(f"//a[@name='{link.access_name}']")
                    for ele in element:
                        if (not ele.text.startswith(
                                '\n') and ele.text == link.access_tab_button_string) or ele.text.startswith('\n'):
                            ele.attrib.update({'class': 'd-none'})
                for link in button.access_kanban_button_ids:
                    element = doc.xpath(f"//button[@name='{link.access_name}']")
                    for ele in element:
                        # if not ele.text.startswith('\n'):
                        ele.attrib.update({'class': 'd-none'})
            view_ref['arch'] = etree.tostring(doc, encoding='unicode')

        # Make whole system readonly
        readonly_access_id = self.env['user.management'].sudo().search(
            [('active', '=', True), ('access_user_ids', 'in', self.env.user.id),
             ('access_readonly', '=', True), ('access_company_ids', 'in', lst)])
        if readonly_access_id:
            doc.attrib.update({'create': 'false', 'delete': 'false', 'edit': 'false', 'duplicate': 'false'})
            view_ref['arch'] = etree.tostring(doc, encoding='unicode').replace('&amp;quot;', '&quot;')
        else:
            # Change model access like :- Create, Update , Delete etc.
            change_model_access = self.env['model.access'].sudo().search([
                ('access_user_manager_id.access_user_ids', 'in', self.env.user.id),
                ('access_user_manager_id.active', '=', True),
                ('access_model_id.model', '=', view_ref['model']), ('access_user_manager_id.access_company_ids', 'in', lst)])
            if change_model_access:
                delete = 'true'
                edit = 'true'
                create = 'true'
                duplicate = 'true'
                for remove_action_ids in change_model_access:
                    if remove_action_ids.access_hide_create:
                        create = 'false'
                    if remove_action_ids.access_hide_edit:
                        edit = 'false'
                    if remove_action_ids.access_hide_delete:
                        delete = 'false'
                    if remove_action_ids.access_hide_duplicate:
                        duplicate = 'false'
                    if remove_action_ids.access_model_readonly:
                        create, delete, edit = 'false', 'false', 'false'
                doc.attrib.update(
                    {'create': create, 'delete': delete, 'edit': edit, 'duplicate': duplicate})
                view_ref['arch'] = etree.tostring(doc, encoding='unicode')
        return view_ref

    def access_hide_field(self, doc, view_ref):
        company_lst = [int(x) for x in request.httprequest.cookies.get('cids').split(',')]
        hidden_fields = self.env['field.access'].sudo().search(
            [('access_model_id.model', '=', self._name),
             ('access_user_manager_id.active', '=', True),
             ('access_user_manager_id.access_user_ids', 'in', self._uid),
             ('access_user_manager_id.access_company_ids', 'in', company_lst)
             ])
        for hide_field in hidden_fields:
            for field_id in hide_field.access_field_id:
                element = doc.xpath(f"//field[@name='{field_id.name}']")
                if element:
                    for ele in element:
                        if hide_field.access_field_invisible:
                            # ele['invisible'] = True
                            ele.set('invisible', '1')
                        if hide_field.access_field_readonly:
                            # ele['readonly'] = True
                            ele.set('readonly', '1')
                            ele.set('force_save', '1')
                        if hide_field.access_field_required:
                            # ele['required'] = True
                            ele.set('required', '1')
                element = doc.xpath(f"//label[@for='{field_id.name}']")
                if element:
                    for ele in element:
                        if ele.get('name') == field_id.name or (ele.tag == 'label' and 'for' in ele.attrib.keys() and ele.attrib['for'] == field_id.name):
                            ele.set('invisible', '1')
        view_ref['arch'] = etree.tostring(doc, encoding='unicode')

    def access_hide_page(self, doc):
        company_lst = [int(x) for x in request.httprequest.cookies.get('cids').split(',')]
        hide_tab_ids = self.env['button.tab.access'].sudo().search(
            [('access_model_id.model', '=', self._name),
             ('access_user_manager_id.active', '=', True),
             ('access_user_manager_id.access_user_ids', 'in', self._uid),
             ('access_user_manager_id.access_company_ids', 'in', company_lst)])

        tabs_ids = hide_tab_ids.mapped('access_hide_tab_ids')
        if tabs_ids:
            for tab in tabs_ids:
                element = doc.xpath(f"//page[@string='{tab.access_tab_button_string}']")
                if element:
                    for ele in element:
                        if ele.attrib.get('name'):
                            if tab.access_name == ele.attrib.get('name'):
                                ele.set('invisible', '1')
                                if 'attrs' in ele.attrib.keys() and ele.attrib['attrs']:
                                    del ele.attrib['attrs']
        return None

    def access_hide_button(self, doc, view_ref):
        """Hide button which is selected inside profile management/button tab access"""
        lst = [int(x) for x in request.httprequest.cookies.get('cids').split(',')]
        hide_button_ids = self.env['button.tab.access'].sudo().search([
            ('access_model_id.model', '=', view_ref['model']), ('access_user_manager_id.active', '=', True),
            ('access_user_manager_id.access_user_ids', 'in', self._uid),
            ('access_user_manager_id.access_company_ids', 'in', lst)])
        for button in hide_button_ids:
            for btn in button.access_hide_button_ids:
                element = doc.xpath(f"//a[@name='{btn.access_name}']")
                for ele in element:
                    # if not ele.text.startswith('\n'):
                    ele.attrib.update({'class': 'd-none'})
                element = doc.xpath(f"//button[@name='{btn.access_name}']")
                for ele in element:
                    # if not ele.text.startswith('\n'):
                    ele.attrib.update({'class': 'd-none'})
                element = doc.xpath(f"//object[@name='{btn.access_name}']")
                for ele in element:
                    # if not ele.text.startswith('\n'):
                    ele.attrib.update({'class': 'd-none'})
            for link in button.access_kanban_button_ids:
                if link.access_button_type == 'edit':
                    element = doc.xpath("//a[@type='edit']")
                elif link.access_button_type == 'set_cover':
                    element = doc.xpath("//a[@type='set_cover']")
                else:
                    element = doc.xpath(f"//a[@name='{link.access_name}']")
                for ele in element:
                    if (not ele.text.startswith(
                            '\n') and ele.text == link.access_tab_button_string) or ele.text.startswith('\n'):
                        ele.attrib.update({'class': 'd-none'})
            for link in button.access_kanban_button_ids:
                element = doc.xpath(f"//button[@name='{link.access_name}']")
                for ele in element:
                    # if not ele.text.startswith('\n'):
                    ele.attrib.update({'class': 'd-none'})
        view_ref['arch'] = etree.tostring(doc, encoding='unicode')

    def access_hide_filter_groupby(self, doc):
        company_lst = [int(x) for x in request.httprequest.cookies.get('cids').split(',')]
        hide_filter_ids = self.env['filter.group.access'].sudo().search(
            [('access_model_id.model', '=', self._name),
             ('access_user_manager_id.active', '=', True),
             ('access_user_manager_id.access_user_ids', 'in', self._uid),
             ('access_user_manager_id.access_company_ids', 'in',
              company_lst)])
        filter_ids = hide_filter_ids.mapped('access_hide_filter_ids')
        if filter_ids:
            for filter in filter_ids:
                element = doc.xpath(f"//filter[@string='{filter.access_filter_group_string}']")
                if element:
                    for ele in element:
                        ele.set('invisible', '1')
                        if 'attrs' in ele.attrib.keys() and ele.attrib['attrs']:
                            del ele.attrib['attrs']
        group_ids = hide_filter_ids.mapped('access_hide_group_ids')
        if group_ids:
            for group in group_ids:
                element = doc.xpath(f"//filter[@string='{group.access_filter_group_string}']")
                if element:
                    for ele in element:
                        ele.set('invisible', '1')
                        if 'attrs' in ele.attrib.keys() and ele.attrib['attrs']:
                            del ele.attrib['attrs']
        return doc
