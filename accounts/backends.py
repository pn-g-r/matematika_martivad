from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

class PhoneOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD) or kwargs.get('phone_number')
        if username is None or password is None:
            return None

        username_str = str(username).strip()
        try:
            user = UserModel.objects.filter(
                Q(username__iexact=username_str) | Q(phone_number=username_str)
            ).first()
            if user is None:
                UserModel().set_password(password)
                return None
        except Exception:
            UserModel().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
