from functools import wraps
from flask import abort
from flask_login import current_user
from flask import flash


#-管理员可访问
def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return func(*args, **kwargs)
    return wrapper
