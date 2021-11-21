"""

    Flask Website Template
    By: Isaac Lehman
    ---
    All views are in this file
    DB and Flask setup are in setup/__init__.py


    Route Structure:
        - LOGGING
        - LOGIN/LOGOUT/SIGNUP
        - HOME
        - GENERAL PAGES
        - BLOG CONTENT
        - POST ENDPOINTS
        - EDITOR
        - SITEMAP
        - ERRORS

"""
from flask import (
    session, 
    request,
    redirect, 
    url_for,
    render_template,
    flash,
    jsonify,
    make_response
)
from urllib.parse import unquote_plus
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlparse
from setup import Privileges, Active_Status, Status
from setup import User, Post, Category, Tag, Option, Comment
from setup import getUser, add_user, get_user__first, set_user__active_status
from setup import get_post__all, get_posts__category, get_posts__tag, get_post_slug__first, get_post_latest__first
from setup import get_tag__first
from setup import get_category__first
from setup import get_option, update_option
from setup import ACCESS_LEVEL, LOG_IN_STATUS
from setup import app, db, IP, PORT
from setup import login_required, admin_required
from setup import send_new_post_email
from setup import get_server_stats
from setup import sendSMS

''' ************************************************************************ '''
'''                               ROUTE HANDLERS                             '''
''' ************************************************************************ '''

# ==================================
#  LOGGING
# ==================================
@app.before_request
def log_visit():    
    if request.endpoint not in [ 'static', 'admin.static' ]:
        num_page_views = Option.query.filter_by(key='num_page_views').first()
        if num_page_views:
            num_page_views.value = str( int(num_page_views.value) + 1 )
            db.session.commit()
        else:
            new_option = Option(key='num_page_views', value='1')
            db.session.add(new_option)
            db.session.commit()

    return

# ==================================
#  LOGIN/LOGOUT/SIGNUP
# ==================================

''' page handlers '''
#https://techmonger.github.io/10/flask-simple-authentication/
### LOGIN ###
# login page
@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        if not (username and password):
            flash("Username or Password cannot be empty.")
            return redirect(url_for('login'))
        else:
            username = username.strip()
            password = password.strip()

        # Get user from database
        possible_user = get_user__first(username)    

        if possible_user and check_password_hash(possible_user.password, password):
            session[LOG_IN_STATUS] = username
            set_user__active_status(username, Active_Status.ACTIVE)

            # set privilege
            session[ACCESS_LEVEL] = possible_user.privilege
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password.")

    return render_template("login.html")


### LOGOUT ###
@app.route("/logout/")
@login_required
def logout():
    set_user__active_status(session[LOG_IN_STATUS], Active_Status.INACTIVE)

    # clear session variables
    session.pop(LOG_IN_STATUS, None)
    session.pop(ACCESS_LEVEL, None)
    
    flash("successfully logged out.")
    # send user back to login page
    return redirect(url_for('login'))


### SIGN UP ###
# signup page
@app.route("/signup/", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email    = request.form.get('email',    None)
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        subscribe= request.form.get('email-subscribe', False)

        get_notifications = 'No'
        if subscribe:
            get_notifications = 'Yes'

        if not (email and username and password):
            flash("Email, Username and Password are required")
            return redirect(url_for('signup'))
        else:
            email    = email.strip()
            username = username.strip()
            password = password.strip()

        # Returns salted pwd hash in format : method$salt$hashedvalue
        hashed_pwd = generate_password_hash(password, 'sha256')

        if not add_user(email, username, hashed_pwd, gets_email=get_notifications):
            flash("Username '{u}' and/or Email '{e}' are not available.".format(u=username, e=email))
            return redirect(url_for('signup'))

        # Send SMS notification for new user
        sendSMS(f'New user!\nUN: {username}\nEMAIL: {email}\nNOTIFICATIONS: {subscribe}', get_option('site-author-phone'))


        flash("User account has been created.")
        return redirect(url_for("login"))
    # if GET
    return render_template("signup.html")


# ==================================
#  HOME
# ==================================

### HOME ###
# home page
@app.route("/", methods=["GET"])
def home():
    all_categories = Category.query.order_by(Category.name.desc()).all()
    all_tags       = Tag.query.order_by(Tag.name.desc()).all()
    latest_post    = Post.query.order_by(Post.publish_date.desc()).limit(1).one()
    return render_template("home.html", all_categories=all_categories, all_tags=all_tags, latest_post=latest_post)


# ==================================
#  GENERAL PAGES
# ==================================

### ABOUT ###
# about page
@app.route("/about/", methods=["GET"])
def about():
    return render_template("about.html")


### PRIVACY ###
# about page
@app.route("/privacy/", methods=["GET"])
def privacy():
    return render_template("privacy.html")


# ==================================
#  BLOG CONTENT
# ==================================

def get_pagination():
    try:
        page     = int(request.args.get('page', 1))
        per_page = int(request.args.get('size', 5))
    except:
        page = 1
        per_page = 5
    return page, per_page

### BLOG ###
# Main page
@app.route("/blog/", methods=["GET"])
def blog():
    page, per_page = get_pagination()
    posts    = get_post__all().paginate(page, per_page, error_out=False)
    # access posts with posts.items
    return render_template("blog.html", posts=posts, title="Blog")


### BLOG - Category ###
@app.route("/blog/categories/<category>/", methods=["GET"])
def blog__category(category):
    page, per_page = get_pagination()
    posts    = get_posts__category(category).paginate(page, per_page, error_out=False)
    cat_name = get_category__first(category)
    if cat_name:
        cat_name = cat_name.name
    else:
        cat_name = "" # error name
    return render_template("blog.html", posts=posts, category=category, title=cat_name)


### BLOG - Tag ###
@app.route("/blog/tags/<tag>/", methods=["GET"])
def blog__tag(tag):
    page, per_page = get_pagination()
    posts    = get_posts__tag(tag).paginate(page, per_page, error_out=False)
    tag_name = get_tag__first(tag)
    if tag_name:
        tag_name = tag_name.name
    else:
        tag_name = "" # error name
    return render_template("blog.html", posts=posts, tag=tag, title=tag_name)


### BLOG SINGLE ###
@app.route("/blog/<slug>/", methods=["GET"])
def blog__single(slug):
    post = get_post_slug__first(slug)
    # Incriment post view count
    if post and post.num_views:
        post.num_views += 1
        db.session.commit()
    elif post:
        post.num_views = 1
        db.session.commit()
    return render_template("blog-single.html", post=post, slug=slug)


# ==================================
#  POST ENDPOINTS
# ==================================

### GET OPTION ###
@admin_required
@app.route('/api/v1/option/<key>/', methods=['GET'])
def get_option__API(key):
    """
        Call:   GET /api/v1/option/API_KEY/
        Return: 1234...
    """
    option_found = get_option(unquote_plus(key))
    if option_found:
        return option_found, 200
    else:
        return None, 404


### ADD/UPDATE OPTION ###
@admin_required
@app.route('/api/v1/option__add/', methods=['POST'])
def add_option__API():
    """
        Call:   POST /api/v1/option__add/
        Data:
            name  = key
            value = value
        Return: 200 or 404
    """
    if len(request.form) < 1:
        return 404
    else:
        request_dict = request.form.to_dict()
        key          = list(request_dict.keys())[0]
        value        = request_dict[key]
        update_option(key, value)

        # TODO: Edit front end to submit using ajax and remove the redirect
        return redirect('/admin/')
        #return f"{key} -> {value}", 200

### GET COMMENTS ###
@app.route('/api/v1/comment/<slug>/<slug2>/', methods=['GET'])
@app.route('/api/v1/comment/<slug>/', methods=['GET'])
def get_comment_slug__API(slug, slug2=None) :
    """
        Call:   GET /api/v1/comment/slug/
        Return: {Comment} in JSON
    """
    try:
        post_slug = slug
        if slug2:
            post_slug = slug2

        post = Post.query.filter_by(slug=post_slug).first()

        all_comments = Comment.query.filter_by(post_id=post.id).all()
        all_comments_JSON = {"data":[]}

        for comment in all_comments:
            all_comments_JSON["data"].append((comment.get_JSON()))

        return jsonify(all_comments_JSON)
    except Exception:
         return jsonify({"data":[]})
    


### ADD COMMENTS ###
@login_required
@app.route('/api/v1/comment/<slug>/<slug2>/', methods=['POST'])
@app.route('/api/v1/comment/<slug>/', methods=['POST'])
def add_comment__API(slug, slug2=None) :
    """
        Call:   GET /api/v1/comment/slug/
        Return: {Comment} in JSON
    """
    
    try:
        post_slug = slug
        if slug2:
            post_slug = slug2

        if len(request.json) < 1:
            return 404
        else:
            request_dict = request.json
            post = Post.query.filter_by(slug=post_slug).first()
            current_user = User.query.filter_by(username=getUser()).first()       
            body = request_dict.get('body', None)
            reCAPTCHA_score = request_dict.get('reCAPTCHA', None)

            new_comment = Comment(author=current_user, post=post, body=body, reCAPTCHA_score=reCAPTCHA_score)
            db.session.add(new_comment)
            db.session.commit()

            # Send SMS notification for new comment
            sendSMS(f'New comment!\nBY: {current_user.username}\nON: {post.title}\nLINK: https://isaacstechblog.com/blog/{post.slug}/', get_option('site-author-phone'))

            return jsonify(new_comment.get_JSON())
    except Exception:
         return jsonify({"data":[]})


### SEND NEW POST EMAIL ###
@admin_required
@app.route('/api/v1/send-new-post/', methods=['GET'])
def send_new_post_email__API():
    """
        Call:   GET /api/v1/send-new-post/
        Return: Sent
    """
    latest_post = get_post_latest__first()
    return send_new_post_email(latest_post)


### GET SERVER STATS
@admin_required
@app.route('/api/v1/server-stats/', methods=['GET'])
def get_server_stats__API():
    """
        Call:   GET /api/v1/server-stats/
        Return: JSON
    """
    server_stats = get_server_stats()
    if server_stats:
        return jsonify(server_stats)
    
    return "ERROR GETTING STATS"


### PAGE SPECIFC SETTINGS (add css/js on each page)
# TODO


# ==================================
#  EDITOR ENDPOINTS
# ==================================
### BLOG SINGLE ###
@app.route("/post-editor/", methods=["GET"])
def post_editor():
   
    return render_template("post-editor.html")


# ==================================
#  SITEMAP ENDPOINTS
#  CREDIT: https://gist.github.com/Julian-Nash/aa3041b47183176ca9ff81c8382b655a
# ==================================
@app.route("/sitemap")
@app.route("/sitemap/")
@app.route("/sitemap.xml")
def sitemap():
    """
        Route to dynamically generate a sitemap of your website/application.
        lastmod and priority tags omitted on static pages.
        lastmod included on dynamic content such as blog posts.
    """
    host_base = 'https://isaacstechblog.com'

    # Static routes with static content 
    static_urls = list()
    for rule in app.url_map.iter_rules():
        if not str(rule).startswith("/admin") and not str(rule).startswith("/sitemap") and not str(rule).startswith("/api") and not str(rule).startswith("/post-editor") and not str(rule).startswith("/logout"):
            if "GET" in rule.methods and len(rule.arguments) == 0:
                url = {
                    "loc": f"{host_base}{str(rule)}"
                }
                static_urls.append(url)

    # Dynamic routes with dynamic content
    dynamic_urls = list()
    blog_posts = Post.query.filter_by(status=Status.PUBLISHED)
    for post in blog_posts:
        url = {
            "loc": f"{host_base}/blog/{post.slug}/",
            "lastmod": post.publish_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        dynamic_urls.append(url)

    xml_sitemap = render_template("sitemap.xml", static_urls=static_urls, dynamic_urls=dynamic_urls, host_base=host_base)
    response = make_response(xml_sitemap)
    response.headers["Content-Type"] = "application/xml"

    return response



# ==================================
#  ERRORS
# ==================================

''' errors handlers '''
@app.errorhandler(400)
def page_not_found_400(e):
    return render_template("error.html", code=404, description="You Made A Bad Request"), 400


@app.errorhandler(401)
def page_not_found_401(e):
    return render_template("error.html", code=404, description="Unauthorized Access"), 401


@app.errorhandler(403)
def page_not_found_403(e):
    return render_template("error.html", code=404, description="Access Forbidden"), 403


@app.errorhandler(404)
def page_not_found_404(e):
    return render_template("error.html", code=404, description="Page Not Found"), 404


@app.errorhandler(500)
def page_not_found_500(e):
    return render_template("error.html", code=500, description="Internal Server Error"), 500



if __name__ == "__main__":
    # TODO: set the way you would like to run the app
    app.run(debug=True, host=IP, port=PORT) # DEBUG MODE
    #app.run(threaded=True, host=IP, port=PORT) # STANDARD FLASK

# Having debug=True allows possible Python errors to appear on the web page
# run with $> python server.py
