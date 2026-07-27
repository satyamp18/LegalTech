from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserModelTests(TestCase):
    def test_create_user_with_roles(self):
        lawyer = User.objects.create_user(
            username="lawyer_test",
            email="lawyer@test.com",
            password="pass",
            role=User.Role.LAWYER
        )
        self.assertTrue(lawyer.is_lawyer)
        self.assertFalse(lawyer.is_admin)

        admin = User.objects.create_user(
            username="admin_test",
            email="admin@test.com",
            password="pass",
            role=User.Role.ADMIN
        )
        self.assertTrue(admin.is_admin)
        self.assertTrue(admin.is_lawyer)
