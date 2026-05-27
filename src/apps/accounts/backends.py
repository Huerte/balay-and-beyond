from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class EmailBackend(ModelBackend):
    """
    Custom authentication backend to allow users to log in using their email address.
    This also handles case-insensitive email lookups (e.g. Admin@example.com = admin@example.com).
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # The AuthenticationForm passes the email via the 'username' kwarg
        email = kwargs.get('email', username)
        
        if not email:
            return None
            
        try:
            # Case-insensitive lookup for better UX
            user = UserModel.objects.get(email__iexact=email)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing difference 
            # between an existing and a non-existing user (prevents timing attacks)
            UserModel().set_password(password)
            return None
            
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
            
        return None
