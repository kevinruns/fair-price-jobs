from flask import flash, redirect, url_for, session, Response
from functools import wraps
from typing import Callable, Any, Optional, Union



        
def apology(message: str, code: int = 400) -> None:
    """Flash an error message.""" 
    flash(message, "error")
    return None  # Return None instead of redirecting




def login_required(f: Callable) -> Callable:
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Union[Response, Any]:
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function




#api requests TBD