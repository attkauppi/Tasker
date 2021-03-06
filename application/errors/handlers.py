from flask import render_template
from application import db
from application.errors import bp


@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    print("Error 500 occurred! Rolled back")
    db.session.rollback()
    return render_template('errors/500.html'), 500

@bp.app_errorhandler(403)
def forbidden(error):
    print("Error 403 occurred, something unauthorized was attempted")
    return render_template('errors/403.html'), 403