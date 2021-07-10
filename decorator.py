from functools import wraps
from flask import session,redirect,url_for

def require_admin(f):
    @wraps(f)
    def wrapped(*args,**kwargs):
        username = session.get("login",None)
        password = session.get("password",None)

        if not username and not password:
            return redirect(url_for("login"))

        return  f(*args,**kwargs)
    return wrapped