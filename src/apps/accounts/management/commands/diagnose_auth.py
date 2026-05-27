from django.core.management.base import BaseCommand
from django.contrib.auth import authenticate, get_user_model
from django.conf import settings

User = get_user_model()


class Command(BaseCommand):
    help = 'Diagnose authentication issues'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str)
        parser.add_argument('password', type=str)

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']

        self.stdout.write(f"\n--- Auth Diagnostic ---")
        self.stdout.write(f"AUTHENTICATION_BACKENDS: {settings.AUTHENTICATION_BACKENDS}")
        self.stdout.write(f"USERNAME_FIELD: {User.USERNAME_FIELD}")

        # Step 1: Does the user exist?
        try:
            user = User.objects.get(email__iexact=email)
            self.stdout.write(self.style.SUCCESS(f"User found: {user.email} (pk={user.pk})"))
            self.stdout.write(f"  is_active: {user.is_active}")
            self.stdout.write(f"  has_usable_password: {user.has_usable_password()}")
            self.stdout.write(f"  password hash (first 40): {user.password[:40]}")
            self.stdout.write(f"  password hash length: {len(user.password)}")
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"No user with email '{email}' exists!"))
            return

        # Step 2: Does check_password work?
        pw_ok = user.check_password(password)
        self.stdout.write(f"  check_password('{password}'): {pw_ok}")

        # Step 3: Does authenticate work?
        result = authenticate(username=email, password=password)
        self.stdout.write(f"  authenticate() result: {result}")

        if result:
            self.stdout.write(self.style.SUCCESS("\nLogin SHOULD work."))
        else:
            self.stdout.write(self.style.ERROR("\nLogin WILL fail. See above for which step returned False/None."))
