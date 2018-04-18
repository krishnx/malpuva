from flask import Flask, url_for, redirect, render_template, request, abort, json
from flask_admin import Admin, helpers, expose, BaseView
from os import linesep, path
from flask_admin.contrib.sqla import ModelView
from local_database import L_DAO
from database import DAO
from app_database import db

from logger_mod import Logger

from datetime import date
from flask_admin.model import typefmt

from time import time

# login utility
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user
from flask_security.forms import RegisterForm, StringField, Required

start = time()

# Date format customization.
def date_format(_, value):
    return value.strftime('%d.%m.%Y')

MY_DEFAULT_FORMATTERS = dict(typefmt.BASE_FORMATTERS)
MY_DEFAULT_FORMATTERS.update({
        type(None): typefmt.null_formatter,
        date: date_format
    })

Logger.logger.info("Start reading from local database.")

# Fetch the data from the local db.
local_db = L_DAO()

database_uri = local_db.execute_query("select * from database_uri;")

# Get all the common properties for tables.
global_table_properties = local_db.execute_query("select * from global_table_properties;")

# Get the table content.
table_column = local_db.execute_query("select * from  table_column;")

# Get the table names.
database_tables = local_db.execute_query("select * from database_tables;")

# Get custom form data from local db.
app_route_data = local_db.execute_query('''SELECT route, method, inputs, output, route_function, database_name, connection_string, callee_function, db_function
                                           FROM app_routes ar
                                           LEFT JOIN database_uri du ON ar.database_id=du.id;''')
view_classes_data = local_db.execute_query('''SELECT view_class, template, route, endpoint, dd_name
                                              FROM view_classes vc
                                              LEFT JOIN app_routes ar ON vc.app_route_id=ar.id;''')

Logger.logger.info("Finished reading model classes from local database.")
Logger.logger.info("Initializing app.")

# Initialize app and add configurations.
app = Flask(__name__)
app.config['DATABASE_FILE'] = 'sample_db.sql'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Alpha@1234@127.0.0.1/the_databases'

# Populate the database's names with their URIs.
sqlalch_binds = {}
for db_u in database_uri:
    sqlalch_binds[db_u[1]] = db_u[2]
app.config['SQLALCHEMY_BINDS'] = sqlalch_binds

# Login utility
app.config['SECURITY_URL_PREFIX'] = "/admin"
app.config['SECURITY_PASSWORD_HASH'] = "pbkdf2_sha512"
app.config['SECURITY_PASSWORD_SALT'] = "ATGUOHAELKiubahiughaerGOJAEGj"
app.config['SECURITY_LOGIN_URL'] = "/login/"
app.config['SECURITY_LOGOUT_URL'] = "/logout/"
app.config['SECURITY_REGISTER_URL'] = "/register/"
app.config['SECURITY_POST_LOGIN_VIEW'] = "/admin/"
app.config['SECURITY_POST_LOGOUT_VIEW'] = "/admin/"
app.config['SECURITY_POST_REGISTER_VIEW'] = "/admin/"
app.config['SECURITY_RECOVERABLE'] = True

# Flask-Security features
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Misc configurations.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'lolwa'
app.config['SESSION_TYPE'] = 'redis'

Logger.logger.info("Finished initializing app.")

@app.route('/')
def index():
    return render_template('admin/index.html')

# app construction.
admin = Admin(app, name='Admin Portal', base_template='admin/my_master.html', template_mode='bootstrap3')

# Login utility
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('roles_id', db.Integer(), db.ForeignKey('roles.id'))
)

class Roles(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    roles = db.relationship('Roles', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return self.email

# Customize the register form
class ExtendedRegisterForm(RegisterForm):
    first_name = StringField("First Name", [Required()])
    last_name = StringField("Last Name", [Required()])

# Login utility
user_datastore = SQLAlchemyUserDatastore(db, User, Roles)
security = Security(app, user_datastore)

@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        SECURITY_LOGIN_USER_TEMPLATE="security/login_user.html",
        SECURITY_REGISTER_USER_TEMPLATE="security/register_user.html",
        SECURITY_RESET_PASSWORD_TEMPLATE="security/reset_password.html",
        h=helpers,
        get_url=url_for
    )

Logger.logger.info("Preparing the model classes data-structure.")

# The structure to contain the whole data.
models_classes = {}

for odb in database_tables:
    if models_classes.has_key(odb[1]):
        models_classes[odb[1]].append({'table_id': int(odb[0]), 'name': odb[2]})
    else:
        models_classes[odb[1]] = [{'table_id': int(odb[0]), 'name': odb[2]}]

for tc in table_column:
    for dbname in models_classes:
        for mc in models_classes[dbname]:
            if tc[1] == mc['table_id']:
                if mc.has_key('column_list'):
                    mc['column_list'].append(({'name': tc[2], 'type': tc[5], 'pk': tc[4], 'default_sort': tc[6],
                                               'column_searchable_list': tc[7], 'column_filters': tc[8], 'form_column': tc[3]}))
                else:
                    mc['column_list'] = [{'name': tc[2], 'type': tc[5], 'pk': tc[4], 'default_sort': tc[6],
                                          'column_searchable_list': tc[7], 'column_filters': tc[8], 'form_column': tc[3]}]

for gtp in global_table_properties:
    for dbname in models_classes:
        for mc in models_classes[dbname]:
            if gtp[3] == mc['table_id']:
                mc['page_size'] = int(gtp[1])
                mc['column_display_pk'] = gtp[2]


# TAB spaces for the code indentation.
tab_spaces = "    "

# Authentication functions overidden for the View classes(ModelView and BaseView).
login_funcs = []
login_funcs.append(tab_spaces + "def is_accessible(self):")
login_funcs.append(tab_spaces * 2 + "if not current_user.is_active or not current_user.is_authenticated:")
login_funcs.append(tab_spaces * 3 + "return False")
login_funcs.append(tab_spaces * 2 + "# if current_user.has_role('superuser'):")
login_funcs.append(tab_spaces * 3 + "# return True")
login_funcs.append(tab_spaces * 2 + "return True")
login_funcs.append(tab_spaces + "def _handle_view(self, name, **kwargs):")
login_funcs.append(tab_spaces * 2 + "if not self.is_accessible():")
login_funcs.append(tab_spaces * 3 + "if current_user.is_authenticated:")
login_funcs.append(tab_spaces * 4 + "# permission denied")
login_funcs.append(tab_spaces * 4 + "abort(403)")
login_funcs.append(tab_spaces * 3 + "else:")
login_funcs.append(tab_spaces * 4 + "return redirect(url_for('security.login', next=request.url))")


# Iterate over the data retrieved from the database and prepare the models and views.
# Finally add them in the application.
model_members = []
view_members = []
add_view_members = ""
for dbname in models_classes:
    for model in models_classes[dbname]:
        Logger.logger.debug("Preparing table class for {0}.".format(model['name']))
        # Model Class
        model_members = ["class {0}(db.Model):".format(model['name'])]
        model_members.append(tab_spaces + "__bind_key__ = '{0}'".format(dbname))

        # View class
        view_members = ["class {0}_view(ModelView):".format(model['name'])] + login_funcs
        form_column = []
        column_filters = []
        column_searchable_list = []

        if model.has_key('column_list'):
            for mem in model['column_list']:
                is_pk = ", primary_key=True" if mem['pk'] else ""
                model_members.append(tab_spaces + "{0} = db.Column({1}{2})".format(mem['name'], mem['type'], is_pk))

                # The order in which the columns are sorted when moving to other page. Used in pagination.
                if mem['default_sort']:
                    view_members.append(tab_spaces + "column_default_sort = '{0}'".format(mem['name']))

                # List of columns to be visible in the 'create' form.
                form_column.append(mem['name']) if mem['form_column'] else None

                # Filters to be added on the view page.
                column_filters.append(mem['name']) if mem['column_filters'] else None

                # List of columns which will be searched for a keyword.
                column_searchable_list.append(mem['name']) if mem['column_searchable_list'] else None

        # Formating the date to only show the date part in the view page.
        view_members.append(tab_spaces + "column_type_formatters = {0}".format(model['column_type_formatters'])) \
            if model.has_key('column_type_formatters') else None

        # The columns to be visible while inserting a new row in the table.
        view_members.append(tab_spaces + "form_columns = {0}".format(form_column)) \
            if len(form_column) > 0 else None

        # To add filters for columns.
        view_members.append(tab_spaces + "column_filters = {0}".format(column_filters)) \
            if len(column_filters) > 0 else None

        # The columns listed in this list would be searched for the text entered in the Search box.
        view_members.append(tab_spaces + "column_searchable_list = {0}".format(column_searchable_list)) \
            if len(column_searchable_list) > 0 else None

        # The number of results in a page.
        view_members.append(tab_spaces + "page_size = {0}".format(model['page_size']))

        # Set true to show primary key of the table in the view.
        view_members.append(tab_spaces + "column_display_pk = {0}".format(model['column_display_pk']))

        # Add views
        add_view_members = "admin.add_view({0}_view({0}, db.session, name='{0}', endpoint='{0}', category='{1}'))".\
            format(model['name'], dbname)

        # exec the whole
        exec (linesep.join(model_members))
        exec (linesep.join(view_members))
        exec (add_view_members)
        Logger.logger.debug("model classes: ")
        Logger.logger.debug(linesep.join(model_members))
        Logger.logger.debug("view classes: ")
        Logger.logger.debug(linesep.join(view_members))
        Logger.logger.debug("add view classes: ")
        Logger.logger.debug(add_view_members)

Logger.logger.info("Finished preparing the model classes data-structure.")
Logger.logger.info("Starting with stored procedures.")

# Read form template.
with open(path.join('./Project/malpuva/templates/admin/custom_form_template.html')) as cft:
    Logger.logger.info("reading the form template from {0}".format(cft.name))
    cft_content = cft.read()

template_data = local_db.execute_query('''SELECT ar_id, extends, js_files, route, method, div_html, inputs, template, doc_root_template_path
                                          FROM form_template ft
                                          LEFT JOIN app_routes ar ON ft.ar_id=ar.id
                                          LEFT JOIN view_classes vc ON ft.ar_id=vc.app_route_id;''')
for td in template_data:
    content = cft_content
    content = content.replace('###EXTENDS###', td[1])
    content = content.replace('###SP_NAME###', td[3])
    content = content.replace('###METHOD###',  td[4])

    common_div_content = td[5]
    fields_div = []
    div_ele = [ele.strip() for ele in td[6].split(",")]
    if len(div_ele[0]) < 1:
        fields_div.append('''<div> This stored procedure <b><i>{0}</i></b> does not take any inputs.
                             <br/>Click the <b>submit</b> button to execute it and see the output.</div>'''.format(td[3]))
    else:
        for field in div_ele:
            fields_div.append(common_div_content.replace('###FIELD_NAME###', field.split('|')[0]))

    content = content.replace('###DIV###', ''.join(fields_div))

    with open(path.join(td[8], td[7]), 'w') as template_file:
        template_file.write(content)

rtinbound_custom_form_data = []
cf_add_view_members = []

for ard in app_route_data:
    Logger.logger.debug("Preparing Stored procedure class for {0}".format(ard[0]))
    rtinbound_custom_form_data.append("@app.route('/{0}', methods=['{1}'])".format(ard[0], ard[1]))
    rtinbound_custom_form_data.append('def {0}():'.format(ard[4]))
    rtinbound_custom_form_data.append(tab_spaces + "try:")
    params = []
    for i in [item.strip() for item in ard[2].split(',')]:
        i = i.strip().split('|')
        if len(i) < 2: continue
        rtinbound_custom_form_data.append(tab_spaces * 2 + "{0} = request.args.get('{0}_input')".format(i[0]))
        params.append(i)

    if len(params) < 1:
        rtinbound_custom_form_data.append(tab_spaces * 2 + "query = '{0} {1};'".format(ard[7], ard[0]))
        Logger.logger.debug("query for sp class {0}: '{1} {0}'".format(ard[0], ard[7]))
    else:
        query_params = ""
        for param in params:
            if len(param) < 2: continue
            if param[1] == 'int':
                query_params += param[0] + " + ', ' + "
            else:
                query_params += " \"'\" + " + param[0] + " + \"', \" + "

        to_remove = r', '
        index = query_params.rfind(to_remove)
        query_params = query_params[:index] + query_params[index+len(to_remove):]
        rtinbound_custom_form_data.append(
            tab_spaces * 2 + "query = 'use {2}; {0} dbo.{1} ' + ".format(ard[7], ard[0], ard[5]) + query_params + " ';'")

        Logger.logger.debug("query for sp class {1}: 'use {2}; {0} dbo.{1} '".format(ard[7], ard[0], ard[5]) + query_params + " ';'")

    rtinbound_custom_form_data.append(tab_spaces * 2 + "d = DAO('{0}')".format(ard[6]))
    rtinbound_custom_form_data.append(tab_spaces * 2 + "res = d.{0}(query)".format(ard[8]))

    rtinbound_custom_form_data.append(tab_spaces * 2 + "if res != 0:")
    rtinbound_custom_form_data.append(tab_spaces * 3 + "return json.dumps({'result': res, 'status': 'success'})")
    rtinbound_custom_form_data.append(tab_spaces * 2 + "else:")
    rtinbound_custom_form_data.append(tab_spaces * 3 + "return json.dumps({'result': res, 'status': 'failure'})")
    rtinbound_custom_form_data.append(tab_spaces + "except Exception as e:")
    rtinbound_custom_form_data.append(tab_spaces * 2 + "return json.dumps({'result':str(e)})")

for vcd in view_classes_data:
    rtinbound_custom_form_data.append("class {0}(BaseView):".format(vcd[0]))
    rtinbound_custom_form_data += login_funcs
    rtinbound_custom_form_data.append(tab_spaces + "@expose('/')")
    rtinbound_custom_form_data.append(tab_spaces + "def index(self):")
    rtinbound_custom_form_data.append(tab_spaces * 2 + "return self.render('{0}')".format(vcd[1]))

    cf_add_view_members.append("admin.add_view({0}(name='{1}', endpoint='{2}', category='{3}'))".format(vcd[0], vcd[2], vcd[3], vcd[4]))

exec (linesep.join(rtinbound_custom_form_data))
exec (linesep.join(cf_add_view_members))
Logger.logger.debug(linesep.join(rtinbound_custom_form_data))
Logger.logger.debug(linesep.join(cf_add_view_members))

Logger.logger.info("Finished with stored procedures.")
Logger.logger.info("spent {0} time.".format(time() - start))

if __name__ == '__main__':
    with app.app_context():
        db.init_app(app)
    app.run(debug=True, host="localhost", port=5050)