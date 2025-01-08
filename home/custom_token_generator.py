from itsdangerous import URLSafeTimedSerializer
from django.conf import settings

class TokenGenerator:
    def __init__(self):
        self.serializer = URLSafeTimedSerializer(settings.SECRET_KEY)

    def generate_token(self, user):
        return self.serializer.dumps(user.email, salt='password-reset-salt')

    def validate_token(self, token, expiration=3600):  # Token valid for 1 hour
        try:
            email = self.serializer.loads(token, salt='password-reset-salt', max_age=expiration)
        except Exception:
            return None
        return email