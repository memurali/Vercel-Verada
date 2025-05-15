# apps/users/services/auth_service.py

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

User = get_user_model()

class AuthService:
    @staticmethod
    def validate_credentials(email, password):
        try:
            user = User.objects.get(email=email)
            if user.is_active and user.check_password(password):
                return user
        except User.DoesNotExist:
            pass
        return None
