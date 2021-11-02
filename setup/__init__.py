"""
    Flask Website Template
    By: Isaac Lehman

    Requirements:
    - python version 3
    - Run: pip3 install flask waitress werkzeug flask_monitoringdashboard
        - or try with gunicorn

    Options to run server:
    1.
        set FLASK_APP=server.py       (set the current server file to run)
        python -m flask run           (run the server)
    2.
        python server.py              (runs in debug mode)


    Structure:
        - IMPORTS
        - APP SET UP
        - DATABASE SET UP
            DB CONNECTION
            HELPER TABLES/CLASSES
            TABLES
        - DATABASE HELPERS
            GENERAL
            TAG
            OPTION
            CATEGORY
            USER
            POST
        - LOGIN SET UP
        - FLASK-ADMIN SET UP
        - PYTHON FUNCTIONS
        - JINJA FILTERS
        - JINJA FUNCTIONS


"""


''' ************************************************************************ '''
'''                                   IMPORTS                                '''
''' ************************************************************************ '''
# FLASK
from flask import (
    request, 
    session, 
    flash, 
    Flask,
    redirect, 
    url_for
)
# DB/ADMIN
from flask_sqlalchemy import SQLAlchemy
# ---
from flask_admin import Admin, AdminIndexView, expose 
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.contrib.sqla import ModelView
# MARKDOWN
import markdown
from markdown.extensions.toc import TocExtension
# RANDOM
from functools import wraps
from datetime import datetime
from urllib.parse import quote_plus
from html import unescape
from postmarker.core import PostmarkClient
from webdock.webdock import Webdock
import os



''' ************************************************************************ '''
'''                                APP SET UP                                '''
''' ************************************************************************ '''
''' set app, cache time, and session secret key '''
IP                        = '127.0.0.1' #'0.0.0.0'
PORT                      = 1234
SEND_FILE_MAX_AGE_DEFAULT = 0 # no cache
SECRET_KEY                = 'mIRGnpOyF0fpDDXfXdzbgA' # Secret Key for Sessions

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['SEND_FILE_MAX_AGE_DEFAULT']      = SEND_FILE_MAX_AGE_DEFAULT  
app.config["SECRET_KEY"]                     = SECRET_KEY  


# SESSION KEYS
ACCESS_LEVEL  = 'access_level'
LOG_IN_STATUS = 'logged_in'


''' ************************************************************************ '''
'''                              DATABASE SET UP                             '''
''' ************************************************************************ '''

# ==============================================================================
# DB CONNECTION
# ==============================================================================

''' set database path '''
# get the path to the directory this script is in and then one level up
scriptdir = os.path.dirname(os.path.dirname(__file__))
# add the relative path to the database file from there
dbpath = os.path.join(scriptdir, "db/site.db")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + dbpath
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ==============================================================================
# HELPER TABLES/CLASSES
# ==============================================================================

''' create helper tables and classes '''
# Many to Many
tags = db.Table('tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True)
)

class Privileges:
    GENERAL = "GENERAL"
    AUTHOR  = "AUTHOR"
    ADMIN   = "ADMIN"

class Status:
    DRAFT     = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED  = "ARCHIVED"

class Active_Status:
    ACTIVE    = "Yes"
    INACTIVE  = "No"


def markdown_text(text):
    """
        Convert text to markdown
    """
    return markdown.markdown(text, extensions=['tables', 'fenced_code', 'nl2br', 'codehilite', TocExtension(toc_depth ="2-6", baselevel=2)])


# ==============================================================================
# TABLES
# ==============================================================================

''' create the main tables '''
class User(db.Model):
    id                = db.Column(db.Integer, primary_key=True)
    email             = db.Column(db.Text, unique=True, nullable=False)
    username          = db.Column(db.Text, unique=True, nullable=False)
    password          = db.Column(db.Text,              nullable=False)
    privilege         = db.Column(db.Text,              nullable=False, default=Privileges.GENERAL) # Privileges Class = GENERAL, AUTHOR, ADMIN

    # Optional - Text
    first_name        = db.Column(db.Text)
    last_name         = db.Column(db.Text)
    bio               = db.Column(db.Text)

    is_active         = db.Column(db.Text)
    gets_email        = db.Column(db.Text, default='No')


    # Optional - Date
    birth_date        = db.Column(db.DateTime)
    last_publish_date = db.Column(db.DateTime)

    def __repr__(self):
        return '<User %r -> %r>' % (self.username, self.privilege)

    def is_admin(self):
        return self.privilege == Privileges.ADMIN

    def is_author(self):
        return self.privilege == Privileges.AUTHOR


class Post(db.Model):
    id                = db.Column(db.Integer,  primary_key=True)
    slug              = db.Column(db.Text,     nullable=False, unique=True)
    title             = db.Column(db.Text,     nullable=False)
    body              = db.Column(db.Text,     nullable=False)
    description       = db.Column(db.Text)
    status            = db.Column(db.Text,     nullable=False, default=Status.DRAFT) # Draft, Published, Archived
    publish_date      = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    num_views         = db.Column(db.Integer,                   default=0)

    # Foreign Keys
    category_id       = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category          = db.relationship('Category', backref=db.backref('posts', lazy=True))

    author_id         = db.Column(db.Integer,   db.ForeignKey('user.id'), nullable=False)
    author            = db.relationship('User', backref=db.backref('posts', lazy=True))

    tags              = db.relationship('Tag', secondary=tags, lazy='subquery', backref=db.backref('posts', lazy=True))

    def __repr__(self):
        return '<Post %r>' % self.title

    # Returns a pretty comma seperated list of the associated tags in Link form
    def tag_names(self):
        if len(self.tags) > 1:
            all_tags = ""
            index = 0
            for tag in self.tags:
                if index == len(self.tags)-1:
                    all_tags += tag.make_link() + " "
                else:
                    all_tags += tag.make_link() + ", "
                index += 1
            return all_tags
        elif len(self.tags) == 1:
            return self.tags[0].make_link()
        else:
            return ""

    def make_link(self):
        return f'<a href="/blog/{self.slug}/">{self.title}</a>'


# One to One -> Post
class Category(db.Model):
    id                = db.Column(db.Integer, primary_key=True)
    name              = db.Column(db.Text,    unique=True, nullable=False)
    slug              = db.Column(db.Text,    unique=True, nullable=False)

    def __repr__(self):
        return '<Category %r>' % self.name

    def make_link(self):
        return f'<a href="/blog/categories/{self.slug}/">{self.name}</a>'


# Many to Many -> Post
class Tag(db.Model):
    id                = db.Column(db.Integer, primary_key=True)
    name              = db.Column(db.Text,    unique=True, nullable=False)
    slug              = db.Column(db.Text,    unique=True, nullable=False)

    def __repr__(self):
        return '<Tag %r>' % self.name

    def make_link(self):
        return f'<a class="tag" href="/blog/tags/{self.slug}/">{self.name}</a>'


# Custom key -> value pairs
class Option(db.Model):
    id                = db.Column(db.Integer, primary_key=True)
    key               = db.Column(db.Text, unique=True, nullable=False)
    value             = db.Column(db.Text, nullable=False)
    def __repr__(self):
        return f'<Option ({self.key} -> {self.value})>'


# comment db:
# - id
# - body
# - was verified
# - reCAPTCHA score

# # foriegn keys
# - post
# - user

# Adapted From: https://www.gatsbyjs.com/blog/2019-08-27-roll-your-own-comment-system/
class Comment(db.Model):
    id                 = db.Column(db.Integer,  primary_key=True)
    body               = db.Column(db.Text,     nullable=False)
    date               = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    spam               = db.Column(db.Integer)
    reCAPTCHA_score    = db.Column(db.Float)

    # Foreign Keys
    author_id          = db.Column(db.Integer,   db.ForeignKey('user.id'), nullable=False)
    author             = db.relationship('User', backref=db.backref('comments', lazy=True))

    post_id            = db.Column(db.Integer,   db.ForeignKey('post.id'), nullable=False)
    post               = db.relationship('Post', backref=db.backref('comments', lazy=True))

    def __repr__(self):
        return f'<Comment ({self.author.username} -> {self.id} -> {self.post.slug})>'

    def get_JSON(self):
        return {
            "id":self.id,
            "username":self.author.username,
            "slug":self.post.slug,
            "body":self.body,
            "date":self.date,
            "is_spam":self.spam
        }


''' ************************************************************************ '''
'''                                DATABASE HELPERS                          '''
''' ************************************************************************ '''
# ==============================================================================
# GENERAL
# ==============================================================================
def get_data__first(object, filter):
    """
        ex. get_data__first(object=User, filter=User.email.endswith('@example.com'))
    """
    try:
        return object.query.filter(filter).first()
    except:
        return None

def get_data__all(object, filter, orderBy):
    """
        ex. get_data__all(object=User, filter=User.email.endswith('@example.com'), orderBy=User.username)
    """
    try:
        return object.query.filter(filter).order_by(orderBy).all()
    except:
        return None

def format_dateTime(date_time):
    return date_time.strftime("%B %d, %Y")


# ==============================================================================
# TAG
# ==============================================================================
def add_tag(name, slug):
    """
        Adds a new Tag
        ex. add_tag('Sauce', 'sauce')
    """
    try:
        new_tag = Tag(name=name, slug=slug)
        db.session.add(new_tag)
        db.session.commit()
        return new_tag
    except:
        return None

def remove_tag(name):
    """
        Remove a Tag
        ex. remove_tag('Sauce')
    """
    try:
        old_tag = Tag.query.filter_by(name=name).first()
        db.session.delete(old_tag)
        db.session.commit()
        return old_tag
    except:
        return None

def get_tag__first(slug):
    """
        Returns the tag object
        ex. get_tag__first('hot')
    """
    try:
        tag_found = Tag.query.filter_by(slug=slug).first()
        return tag_found
    except:
        return None

def get_tag__all():
    """
        Returns all tags
        ex. get_tag__all()
    """
    try:
        return Tag.query.all()
    except:
        return None


# ==============================================================================
# OPTION
# ==============================================================================
def add_option(key, value):
    """
        Adds a new Option
        ex. add_option('API_KEY', '1234567890')
    """
    try:
        new_option = Option(key=key, value=str(value))
        db.session.add(new_option)
        db.session.commit()
        return new_option
    except:
        return None

def remove_option(key):
    """
        Remove an Option
        ex. remove_option('Sauce')
    """
    try:
        old_option = Option.query.filter_by(key=key).first()
        db.session.delete(old_option)
        db.session.commit()
        return old_option
    except:
        return None

def get_option(key, default=None):
    """
        Returns the value in a key value pair
        ex. get_option('API_KEY')
    """
    try:
        option_found = Option.query.filter_by(key=key).first()
        return option_found.value
    except:
        if default:
            return default
        return None

def get_option__obj(key):
    """
        Returns the object 
        ex. get_option__obj('API_KEY')
    """
    try:
        option_found = Option.query.filter_by(key=key).first()
        return option_found
    except:
        return None

def get_option__all():
    """
        Returns all options
        ex. get_option__all()
    """
    try:
        return Option.query.all()
    except:
        return None

def update_option(key, value):
    old_option = get_option__obj(key)
    if old_option:
        old_option.value = value
        db.session.commit()
        return old_option
    else: 
        return add_option(key, value)

# ==============================================================================
# CATEGORY
# ==============================================================================
def add_category(name, slug):
    """
        Adds a new Category
        ex. add_category('Cooking', 'cooking')
    """
    try:
        new_category = Category(name=name, slug=slug)
        db.session.add(new_category)
        db.session.commit()
        return new_category
    except:
        return None

def remove_category(name):
    """
        Remove a Category
        ex. remove_category('Cooking')
    """
    try:
        old_category = Category.query.filter_by(name=name).first()
        db.session.delete(old_category)
        db.session.commit()
        return old_category
    except:
        return None

def get_category__first(slug):
    """
        Returns the category object
        ex. get_category__first('Hot')
    """
    try:
        return Category.query.filter_by(slug=slug).first()
    except:
        return None

def get_category__all():
    """
        Returns all categories
        ex. get_category__all()
    """
    try:
        return Category.query.all()
    except:
        return None


# ==============================================================================
# USER
# ==============================================================================
def add_user(email, username, password, first_name=None, last_name=None, bio=None, birth_date=None, last_publish_date=None, privilege="GENERAL", gets_email='No'):
    """
    Fields:
        add_user(email, username, password, first_name=None, last_name=None, bio=None, birth_date=None, last_publish_date=None)
    """
    try:
        new_user = User(email=email, username=username, password=password, is_active=Active_Status.INACTIVE, first_name=first_name, last_name=last_name, bio=bio, birth_date=birth_date, last_publish_date=last_publish_date, privilege=privilege, gets_email=gets_email)
        db.session.add(new_user)
        db.session.commit()
        return new_user
    except:
        return None

def remove_user(username):
    """
        Removes the user with a given username
        ex. remove_user('joe')
    """
    try:
        old_user = User.query.filter_by(username=username).first()
        db.session.delete(old_user)
        db.session.commit()
        return old_user
    except Exception as e:
        return None

def get_user__first(username, password=None):
    """
        Returns the user with a given username (optional password)
        ex. get_user__first('joe')
    """
    try:
        if not password:
            return User.query.filter_by(username=username).first()
        else:
            return User.query.filter_by(username=username, password=password).first()
    except:
        return None

def get_user__all():
    """
        Returns all users
        ex. get_user__all()
    """
    try:
        return User.query.all()
    except:
        return None

def get_users__privilege(privilege):
    """
        Returns all users with a given Privlege
        ex. get_users__privilege('ADMIN')
    """
    try:
        return User.query.filter_by(privilege=privilege).all()
    except:
        return None

def set_user__last_publish_date(username, date):
    """
        Sets the users last publication date
        - ex. set_user__last_publish_date(author.username, new_post.publish_date)
    """
    try:
        updated_user = get_user__first(username)
        updated_user.last_publish_date = date
        db.session.commit()
        return True
    except:
        return None

def set_user__active_status(username, status):
    """
        Sets the users active status
        - ex. set_user__active_status(username, Active_Status.ACTIVE)
    """
    try:
        updated_user = get_user__first(username)
        updated_user.is_active = status
        db.session.commit()
        return True
    except:
        return None


# ==============================================================================
# POST
# ==============================================================================
def add_post(title, body, category, author, slug, status=Status.DRAFT):
    """
    Fields:
        add_post(title, body, category, author)
    """
    try:
        new_post = Post(title=title, body=body, category=category, author=author, slug=slug, status=status) # TODO: get current user

        # Set users last publication date
        set_user__last_publish_date(author.username, new_post.publish_date)

        db.session.add(new_post)
        db.session.commit()
        return new_post
    except:
        return None

def add_post__tag(post, tag):
    """
        ex. add_post__tag(all_posts[0], 'Creamy')
    """
    try:
        post.tags.append(get_tag__first(tag))
        db.session.commit()
    except:
        return None

def remove_post(id):
    """
        Removes the post with a given id
        ex. remove_post(post.id)
    """
    try:
        old_post = Post.query.get(id)
        db.session.delete(old_post)
        db.session.commit()
        return old_post
    except:
        return None

def get_post__first(id):
    """
        Returns the post with a given id
        ex. get_post__first(1234)
    """
    try:
        return Post.query.get(id)
    except:
        return None

def get_post_slug__first(slug):
    """
        Returns the post with a given slug
        ex. get_post_slug__first('cookie-dough')
    """
    try:
        return Post.query.filter_by(slug=slug, status=Status.PUBLISHED).first()
    except:
        return None

def get_post_latest__first():
    """
        Returns the latest post
        ex. get_post_latest__first()
    """
    try:
        return Post.query.order_by(Post.publish_date.desc()).first()
    except:
        return None

def get_post__all():
    """
        Returns all posts (w/o .all())
        ex. get_post__all()
    """
    try:
        return Post.query.filter_by(status=Status.PUBLISHED).order_by(Post.publish_date.desc())
    except:
        return None

def get_posts__title(title):
    """
        Returns all posts with a given title
        ex. get_posts__title('How to read a book')
    """
    try:
        return Post.query.filter_by(title=title, status=Status.PUBLISHED).order_by(Post.publish_date.desc())
    except:
        return None

def get_posts__category(category):
    """
        Returns all posts with a given category slug
        ex. get_posts__category('creamy')
    """
    try:
        return Post.query.filter_by(category=get_category__first(category), status=Status.PUBLISHED).order_by(Post.publish_date.desc())
        #return Post.query.filter_by(category=category).all()
    except:
        return None

def get_posts__tag(tag):
    """
        Returns all posts with a given tag
        ex. get_posts__tag('Hot')
    """
    try:
        return Post.query.filter(Post.tags.any(Tag.slug.contains(tag))).filter(Post.status == Status.PUBLISHED).order_by(Post.publish_date.desc())
    except:
        return None

def get_posts__author(author, is_object=True):
    """
        Returns all posts for a given author (User object or username)
        ex. get_posts__author(author)
        ex. get_posts__author('Joe', False)
    """
    try:
        if is_object:
            return Post.query.filter_by(author=author).all()
        else:
            return Post.query.filter(Post.author.has(User.username.contains(author))).filter(Post.status == Status.PUBLISHED).order_by(Post.publish_date.desc())
    except:
        return None

def get_posts__title(key_word):
        """
            Returns all posts with a title containing a given key_word
            ex. get_posts__title('Make')
        """
        try:
            return Post.query.filter(Post.title.contains(key_word)).filter(Post.status == Status.PUBLISHED).order_by(Post.publish_date.desc())
        except:
            return None

def get_posts__title_and_body(key_word):
        """
            Returns all posts for a given title or body
            ex. get_posts__title_and_body('Make')
        """
        try:
            return Post.query.filter(Post.title.contains(key_word) | Post.body.contains(key_word)).filter(Post.status == Status.PUBLISHED).order_by(Post.publish_date.desc())
        except:
            return None



''' ************************************************************************ '''
'''                              LOGIN SET UP                                '''
''' ************************************************************************ '''
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if LOG_IN_STATUS in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login'))

    return wrap


def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if ACCESS_LEVEL in session and session[ACCESS_LEVEL] == Privileges.ADMIN:
            return f(*args, **kwargs)
        else:
            flash("You don't have access to that page...")
            return redirect(url_for('home'))

    return wrap


def getUser():
    try:
        return session[LOG_IN_STATUS]
    except Exception as e:
        return None

''' ************************************************************************ '''
'''                              FLASK-ADMIN SET UP                          '''
''' ************************************************************************ '''
# set optional bootswatch theme
app.config['FLASK_ADMIN_SWATCH'] = 'yeti'
ADMIN_DISPLAY_TITLE = 'ADMIN'

# ==========================================
# Options that can be set on the Admin page
# ==========================================
all_default_options = [
    {
        'name':'ga-tag',
        'type':'text',
        'default':'1234'
    },
    {
        'name':'site-title',
        'type':'text',
        'default':'Site Title'
    },
    {
        'name':'site-author-name',
        'type':'text',
        'default':'Site Author'
    }, 
    {
        'name':'site-author-email',
        'type':'text',
        'default':'test@example.com'
    },
    {
        'name':'display_file_editor',
        'type':'text',
        'default':'False'
    },
    {
        'name':'reCAPTCHA private key',
        'type':'text',
        'default':''
    },
    {
        'name':'reCAPTCHA public key',
        'type':'text',
        'default':''
    },
    {
        'name':'github-username',
        'type':'text',
        'default':''
    },
    {
        'name':'postmark-api-key',
        'type':'text',
        'default':''
    },
    {
        'name':'webdock-api-key',
        'type':'text',
        'default':''
    },
    {
        'name':'webdock-server-slug',
        'type':'text',
        'default':''
    }
]


# ==========================================
# Model Views for DB tables
# ==========================================
class DASHBOARDModelView(ModelView):
    # Show primary key of tables
    column_display_pk = True

    # allow/disallow users access
    def is_accessible(self):
        return ACCESS_LEVEL in session and session[ACCESS_LEVEL] == Privileges.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

class UserModelView(ModelView):
    # Show primary key of tables
    column_display_pk = True

    column_exclude_list = ['password']
    column_searchable_list = ['username', 'email']
    form_choices = {
        'privilege': [
            (Privileges.GENERAL, 'General'),
            (Privileges.AUTHOR, 'Author'),
            (Privileges.ADMIN, 'Admin')
        ]
    }

    # allow/disallow users access
    def is_accessible(self):
        return ACCESS_LEVEL in session and session[ACCESS_LEVEL] == Privileges.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

class PostModelView(ModelView):
    # Show primary key of tables
    column_display_pk = True

    column_exclude_list = ['body']
    column_searchable_list = ['body', 'title']
    form_choices = {
        'status': [
            (Status.DRAFT, 'Draft'),
            (Status.PUBLISHED, 'Published'),
            (Status.ARCHIVED, 'Archived')
        ]
    }

    # allow/disallow users access
    def is_accessible(self):
        return ACCESS_LEVEL in session and session[ACCESS_LEVEL] == Privileges.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))


# ==========================================
# Create customized index view class 
# ==========================================
class MyHomeView(AdminIndexView):
    @expose('/')
    # Allow all logged in users to view this page
    @login_required
    def index(self):
        return self.render('admin/index.html')

# ==========================================
# Initialize Flask ADMIN + Add views
# ==========================================
admin = Admin(app, name=ADMIN_DISPLAY_TITLE, index_view=MyHomeView(), template_mode='bootstrap4')


# Add administrative views here (i.e. tables)
admin.add_view(UserModelView(User,     db.session))
admin.add_view(PostModelView(Post,     db.session))
admin.add_view(DASHBOARDModelView(Tag,      db.session))
admin.add_view(DASHBOARDModelView(Category, db.session))
admin.add_view(DASHBOARDModelView(Option,   db.session))
admin.add_view(DASHBOARDModelView(Comment,   db.session))


# ==========================================
# Add file viewer/editor 
# (SECURITY VULNERABILITY - KEEP DISABLED UNLESS NECESSARY)
# ==========================================
if(get_option('display_file_editor') == 'True'):    
    class MyFileAdmin(FileAdmin):

        # allow/disallow users access
        def is_accessible_path(self, path):
            return ACCESS_LEVEL in session and session[ACCESS_LEVEL] == Privileges.ADMIN

        editable_extensions = ('md', 'html', 'txt', 'css', 'js')
        
    admin.add_view(MyFileAdmin(app.static_folder, '/static/', name='Static Files'))


''' ************************************************************************ '''
'''                               PYTHON FUNCTIONS                           '''
''' ************************************************************************ '''

# ==========================================
# POSTMARK
# ==========================================
def send_new_post_email(new_post):
    # send an email to each user that gets emails
    try:
        api_key     = get_option('postmark-api-key')
        admin_email = get_option('site-author-email')
        all_users   = User.query.filter_by(gets_email='Yes').all()
        postmark    = PostmarkClient(server_token=api_key)

        for user in all_users: 
            user_email = user.email

            postmark.emails.send(
                From=admin_email,
                To=user_email,
                Subject="New Post From Isaac's Tech Blog",
                HtmlBody=f"""
                    <h1><a href="https://isaacstechblog.com/blog/{new_post.slug}">{new_post.title}</a></h1>
                    <p>{new_post.description}<p>
                    <small>please contact admin@isaacstechblog.com to unsuscribe.</small>
                """
            )
        return 'Email sent!'
    except Exception:
        return 'ERROR: sending email...'

# ==========================================
# WEBDOCK
# ==========================================
def get_server_stats():
    # Retrieve the last weeks worth of data
    try:
        api_key     = get_option('webdock-api-key')
        server_slug = get_option('webdock-server-slug')
        wd = Webdock(api_key)

        metrics = wd.get_server_metrics(server_slug)

        if metrics.get('status') != 200:
            return None
        all_stats = metrics.get('data')

        return all_stats
    except Exception as e:
        return None

# def process_server_stats():
#     """
#     Returns arrays with {amount, timestamp}
#     """
#     # Get the data
#     sever_stats = get_server_stats()
#     if sever_stats is None:
#         return None

#     # get data groups
#     disk_stats = sever_stats.get('disk')
#     ram_stats  = sever_stats.get('disk')
#     cpu_stats  = sever_stats.get('memory')
    
#     # disk
#     disk_allowed = disk_stats.get('allowed')
#     disk_usage   = disk_stats.get('samplings')

#     # - calculate left (allowed - used)
#     disk_left    = [{(disk_allowed - disk_json.get('amount')), disk_json.get('timestamp')} for disk_json in disk_usage]
#     disk = {
#         'allowed': disk_allowed,
#         'used':list(disk_usage),
#         'left':list(disk_left)
#     }

#     # ram
#     ram_usage    = list(ram_stats.get('usageSamplings'))

#     # cpu
#     cpu_usage    = list(cpu_stats.get('usageSamplings'))

#     return [disk, ram_usage, cpu_usage]






''' ************************************************************************ '''
'''                               JINJA FILTERS                              '''
''' ************************************************************************ '''
# ==========================================
# USAGE:
#   {{ <var> | <filter}}   
# ==========================================


@app.template_filter('make_caps')
def make_caps(text):
    """Convert a string to all caps."""
    return text.uppercase()


@app.template_filter('markdown')
def make_markdown(text):
    """Convert a string to markdown."""
    return markdown_text(text)


@app.template_filter('unescape_HTML')
def unescape_HTML(text):
    """Unescapes HTML Characters."""
    return unescape(text)


@app.template_filter('comma_format')
def comma_format(number):
    """Comma seperate number."""
    return "{:,}".format(number)


@app.template_filter('quote_plus')
def do_quote_plus(text):
    """URL encode"""
    return quote_plus(text)



''' ************************************************************************ '''
'''                               JINJA FUNCTIONS                            '''
''' ************************************************************************ '''
# ==========================================
# USAGE:
#   {{ function(<value>...)}}   
# ==========================================

@app.context_processor
def utility_processor():
    def format_price(amount, currency=u'$'):
        """Formats a currency"""
        return u'{1}{0:.2f}'.format(amount, currency)
    
    def get_option_filter(key, default=None):
        """Returns a the value in a key value option pair"""
        return get_option(key, default=default)

    def get_default_options():
        """Array of {name,type} pairs"""
        # Set defaults
        return all_default_options

    def get_related_post(cat, num_posts, slug):
        """Returns num_posts related posts."""
        #try:
        return Post.query.filter(
                    Post.category == get_category__first(cat)
                ).filter(
                    Post.status == Status.PUBLISHED
                ).filter(
                    Post.slug != slug
                ).order_by(
                    Post.publish_date.desc()
                ).limit(
                    num_posts
                ).all()
        # except Exception:
        #     print("ERROR")
        #     return None

    return dict(format_price=format_price, get_option=get_option_filter, get_default_options=get_default_options, get_related_post=get_related_post)
