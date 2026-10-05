from utils import get_user_model

User = get_user_model()


class AdminAuth:

    def authenticate(self, request, username):

        if request.user.is_staff is False:
            return

        try:
            return User.objects.get(username=username)

        except User.DoesNotExist:
            return

    def get_user(self, user_id):

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return
