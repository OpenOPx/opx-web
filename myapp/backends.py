from myapp.models import User
import logging


class MyAuthBackend(object):
    def authenticate(self, email, password):

        try:
            user = User.objects.filter(useremail__exact = email).filter(password__exact = password)
            if user[0]:
                return user[0]
            else:
                return None
        except User.DoesNotExist:
            logging.getLogger("error_logger").error("user with login does not exists ")
            return None
        except Exception as e:
            logging.getLogger("error_logger").error(repr(e))
            return None

    def get_user(self, user_id):
        try:
            user = User.objects.get(userid=user_id)
            if user:
                return user
            return None
        except User.DoesNotExist:
            logging.getLogger("error_logger").error("user with not found")
            return None
