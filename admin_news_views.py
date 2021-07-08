from flask import render_template,request,redirect, url_for,session,flash
from config import app,OS_UPLOAD_PATH
from models import News,Category,Users,db
from datetime import datetime
import os
from uuid import uuid4
from slugify import slugify
import bcrypt

@app.route("/admin/news/")
def admin_news_list_view():
    username = session.get("login",None)
    password = session.get("password",None)

    if not username and not password:
        return redirect(url_for("login"))
    if ("action" and "_id") in request.args:
        try:
            _id = int(request.args.get("_id"))
        except:
            return redirect(url_for("admin_news_list_view"))

        if request.args.get("action") == "make_active":
            chosen_news = News.query.filter_by(id=_id).first_or_404()
            chosen_news.is_published = True
            db.session.commit()
        elif request.args.get("action") == "make_inactive":
            chosen_news = News.query.filter_by(id=_id).first_or_404()
            chosen_news.is_published = False
            db.session.commit()

        elif request.args.get("action") == "delete" :
            chosen_news = News.query.filter_by(id=_id).first_or_404()
            try:
                os.unlink(os.path.join("static","uploads","images",chosen_news.photo))
            except:
                pass
            db.session.delete(chosen_news)
            db.session.commit()
            return redirect(url_for("admin_news_list_view"))

        else:
            return redirect(url_for("admin_news_list_view"))
    all_news = News.query.order_by(News.id.desc()).all()
    return render_template("admin/news_list.html", yangiliklar = all_news)

@app.route("/admin/news/create/", methods=["GET", "POST"])
def add_news_view():
    username = session.get("login",None)
    password = session.get("password",None)

    if not username and not password:
        return redirect(url_for("login"))
    if request.method == "POST":
        news = News()
        news.title = request.form["news_title"]
        news.content = request.form["news_content"]
        news.slug = slugify(news.title)
        news.ispublished = bool(request.form.get("publish_status", False))

        try:
            news.cat_id = int(request.form.get("category_id"))
        except:
            return redirect(url_for('add_news_view'))
        if "news_photo" in request.files:
            news_photo = request.files["news_photo"]
            photo_filename = str(uuid4()) + "." + news_photo.filename.split(".")[-1]
            news_photo.save(os.path.join("static","uploads","images",photo_filename))
            if news_photo.filename.split(".")[-1] != " S":
                news.photo = photo_filename
        db.session.add(news)
        db.session.commit()
        return redirect(url_for('admin_news_list_view'))

    return render_template("admin/add_news.html")


@app.route("/create-category/", methods = ["GET","POST"])
def add_category_view():
    username = session.get("login",None)
    password = session.get("password",None)

    if not username and not password:
        return redirect(url_for("login"))
    category_name = request.form.get("category_name",None)

    if category_name:
        c = Category()

        c.name = category_name
        db.session.add(c)
        db.session.commit()

    return render_template("client/add_category.html")



@app.route("/admin/news/<int:_id>/" ,methods = ["GET","POST"] )
def update_news_view(_id):
    username = session.get("login",None)
    password = session.get("password",None)

    if not username and not password:
        return redirect(url_for("login"))
    if request.method == "POST":
        news = News.query.filter_by(id = _id).first_or_404()

        news.title = request.form["news_title"]
        news.content = request.form["news_content"]
        news.slug = slugify(news.title)
        news.is_published = bool(request.form.get("publish_status", False))

        try:
            news.cat_id = int(request.form.get("category_id"))
        except:
            return redirect(url_for('update_news_view'))
        if "news_photo" in request.files:
            news_photo = request.files["news_photo"]
            photo_filename = str(uuid4()) + "." + news_photo.filename.split(".")[-1]
            news_photo.save(os.path.join("static","uploads","images",photo_filename))
            if news_photo.filename.split(".")[-1] != " ":
                news.photo = photo_filename
        db.session.commit()

        return redirect(url_for('admin_news_list_view'))

    elif request.method == "GET":
        if request.args.get("action",None) == "delete-thumb":
            chosen_news = News.query.filter_by(id = _id).first_or_404()
            os.unlink(os.path.join("static","uploads","images",chosen_news.photo))
            chosen_news.photo = ""
            db.session.commit()
            return redirect(url_for('update_news_view', _id = _id))
        chosen_news = News.query.filter_by(id = _id).first_or_404()
        return render_template("admin/update_news.html", yangilik = chosen_news)

@app.route("/login/",methods = ["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username",None)
        password = request.form.get("password",None)

        if not username and not password:
            flash("Login yoki parolni noto'gri kiritdingiz!","danger")
        else:
            user = Users.query.filter_by(username=username.strip()).first_or_404()
            if bcrypt.checkpw(password.encode(), user.password):
                flash("Siz kabinetingizga kirdingiz!","success")
                session["login"] = username
                session["password"] = password.strip()
                return redirect(url_for("admin_news_list_view"))
            else:
                flash("Parolni xato terdingiz!","danger")

    return render_template("admin/login.html")


from pprint import pprint
@app.route("/register/", methods = ["GET","POST"])
def register():
    if request.method == "POST":
        fullname = request.form.get("fullname",None)
        password1 = request.form.get("password1",None)
        password2 = request.form.get("password2",None)
        username = request.form.get("username",None)


        if not username:
            flash("Username kiritilmadi!","danger")
        elif password1 and password2 and (password1.strip() != password2.strip()):
            flash("Parollar mos kelmadi!","danger")
        else:   
            user = Users()
            user.username = username
            if fullname:
                user.fullname = fullname
            user.password = bcrypt.hashpw(password1.strip().encode(),bcrypt.gensalt())
            db.session.add(user)
            db.session.commit()
            flash("Siz ro'yhatdan muvafaqqiyatli o'tdingiz!","success")
    return render_template("admin/register.html") 


@app.route("/logout/")
def logout():
    session.pop("login",None)
    session.pop("password",None)
    return redirect(url_for("login"))