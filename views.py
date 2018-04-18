from flask_admin import expose, BaseView
from flask_admin.form import rules
from flask_admin.contrib.sqla import ModelView
from flask_admin.actions import action
from models import test_another_procedures, test_procedures

class MyView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/custom_home.html')

class OldCustomView(ModelView):
    def create_model(self, form):
        one = test_procedures()
        another = test_another_procedures()
        form.populate_obj(one)

        one.input1 = 'one hundred'

        another.input1 = one.input1

        self.session.add(another)
        self.session.commit()

        return True

    # def on_model_change(self, form, model, is_created):
    #     print "on_model_change called."
    #     one = test_procedures()
    #     two = test_another_procedures()
    #     form.populate_obj(two)
    #
    #     print self.scaffold_list_columns()
    #
    #     self.session.add(one)
    #     self.session.commit()
    #
    #     return True

    # def update_model(self, form, model):
    #     print "update_model called."
    #     one = test_procedures()
    #     # form.populate_obj(one)
    #     # print model.input1, model.input2, model.input3
    #     one.input1 = model.input1
    #     one.input2 = model.input2
    #     one.input3 = model.input3
    #
    #     self.session.add(one)
    #     self.session.commit()
    #     return True

    form_create_rules = [
        rules.FieldSet(('input1', 'input2', 'input3'), 'Broker'),
        #rules.FieldSet(('input1', 'input2', 'input3'), 'Investor'),
        #rules.FieldSet(('input1', 'input2', 'input3'), 'Vendor')
    ]

    form_edit_rules = form_create_rules
    create_template = "admin/abc_create.html"
    edit_template = "admin/abc_edit.html"

class LocalCustomForm1(BaseView):
    @expose('/')
    def custom_form1(self):
        return self.render('admin/custom_form1.html')

class LocalCustomForm2(BaseView):
    @expose('/')
    def custom_form1(self):
        return self.render('admin/custom_form2.html')

class LocalCustomForm3(BaseView):
    @expose('/')
    def custom_form2(self):
        return self.render('admin/custom_form3.html')