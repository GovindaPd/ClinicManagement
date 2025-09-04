from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_str, force_bytes
from itsdangerous import URLSafeTimedSerializer




class TokenGenerator:
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)

    @classmethod
    def generate_token(cls, user):
        s = f"{user.custom_id}@{user.last_login}@{user.user_type}"
        return cls.serializer.dumps(s, salt='password-reset-salt')

    @classmethod
    def validate_token(cls, token, expiration=300):  # Token valid for by default 3 days in seconds 60*60*24*3
        """ return decoded string """
        try:
            token_string = cls.serializer.loads(token, salt='password-reset-salt', max_age=expiration)
        except Exception:
            return None
        return token_string

    @staticmethod
    def encode_string(string):
        return urlsafe_base64_encode(force_bytes(string))
    
    @staticmethod
    def decode_string(uuid64):
        return force_str(urlsafe_base64_decode(uuid64))
    
    @staticmethod
    def compare_token(user, token_string):
        user_model = get_user_model()
        if not isinstance(user, user_model):
            raise TypeError(f"object is not instance of {user_model} model")
        
        gen_string = f"{user.custom_id}@{user.last_login}@{user.user_type}"
        return True if gen_string == token_string else False
    


