from django.test import TestCase
from django.urls import reverse

from .models import Privacy
from access.models import CustomUser
from test_util import util, account_util, log_util, settings_util

# Create your tests here.
class PrivacyViewTests(TestCase):
    def setUp(self):
        self.user1 = account_util.create_random_valid_user()
        self.user2 = account_util.create_random_valid_user()
        self.client.force_login(self.user1)
        # self.client.force_login(self.user2)

    def test_default_privacy_is_off(self):
        """
        Default setting for logs should be public
        """
        user1_privacy = Privacy.objects.get(user=self.user1)
        user2_privacy = Privacy.objects.get(user=self.user2)
        self.assertTrue(user1_privacy)
        self.assertTrue(user2_privacy)

    def test_privacy_on(self):
        """
        Users should be able to choose to make their logs private
        """
        form = settings_util.create_log_setting_form(False)
        self.client.post(reverse('settings:privacy'), form)
        privacy_setting = Privacy.objects.get(user=self.user1)
        self.assertFalse(privacy_setting.show_logs)

    def test_privacy_on_then_off(self):
        """
        Users should be able to choose to make their logs public
        """
        on_form = settings_util.create_log_setting_form(False)
        off_form = settings_util.create_log_setting_form(True)
        self.client.post(reverse('settings:privacy'), on_form)
        self.client.post(reverse('settings:privacy'), off_form)
        privacy_setting = Privacy.objects.get(user=self.user1)
        self.assertTrue(privacy_setting.show_logs)


class PrivacyTemplateTests(TestCase):
    def setUp(self):
        self.user1 = account_util.create_random_valid_user()
        self.user2 = account_util.create_random_valid_user()

    def make_current_user_logs_public(self, privacy_value: bool):
        form = settings_util.create_log_setting_form(privacy_value)
        self.client.post(reverse('settings:privacy'), form)

    def test_private_log_detail_hidden_to_unauth_users(self):
        """
        Log detail should provide a message to indicate unauthorized
        view status
        """
        self.client.force_login(self.user1)
        log = log_util.create_random_log(self.user1)
        self.make_current_user_logs_public(False)

        # Login user2 and verify error message renders when accessing that log detail
        self.client.force_login(self.user2)
        response = self.client.get(reverse('logs:detail', args=[log.id]))
        self.assertContains(response, 'do not have permission')

    def test_private_log_detail_not_hidden_to_owner(self):
        """
        Private Log details should NOT be hidden to its own creator
        """
        self.client.force_login(self.user1)
        log = log_util.create_random_log(self.user1)
        self.make_current_user_logs_public(False)

        response = self.client.get(reverse('logs:detail', args=[log.id]))
        self.assertNotContains(response, 'do not have permission')

    def test_private_index_log_hidden(self):
        """
        Private logs should not render at all in logs index, even to owner
        """
        self.client.force_login(self.user1)
        log_util.create_random_log(self.user1)
        self.make_current_user_logs_public(False)

        # Hidden to owner
        response = self.client.get(reverse('logs:index'))
        self.assertNotContains(response, 'log-entry-container')

        # Hidden to unauthorized user
        self.client.force_login(self.user2)
        response = self.client.get(reverse('logs:index'))
        self.assertNotContains(response, 'log-entry-container')

        # Hidden to unathenticated user
        self.client.logout()
        response = self.client.get(reverse('logs:index'))
        self.assertNotContains(response, 'log-entry-container')

    def test_all_user_profile_private_logs_hidden(self):
        """
        Render message indicating unauthorized status for private logs
        The GET response should return no logs to unauthorized users
        """
        self.client.force_login(self.user1)
        log_util.create_random_log(self.user1)
        self.make_current_user_logs_public(False)

        self.client.force_login(self.user2)
        response = self.client.get(reverse('profiles:user', args=[self.user1.id]))
        self.assertContains(response, 'logs are private')

    def test_all_user_profile_logs_unhidden(self):
        """
        All previously private logs should be rendered on profile
        if user resets privacy setting
        """
        self.client.force_login(self.user1)
        log_util.create_random_log(self.user1)
        self.make_current_user_logs_public(False)
        self.make_current_user_logs_public(True)

        self.client.force_login(self.user2)
        response = self.client.get(reverse('profiles:user', args=[self.user1.id]))
        self.assertNotContains(response, 'logs are private')
        self.assertContains(response, 'logs-container')

    def test_all_user_profile_logs_available_to_creator(self):
        """
        All logs, regardless of privacy status, should be rendered on profile page for owner
        """
        self.client.force_login(self.user1)
        log_util.create_random_log(self.user1)
        self.make_current_user_logs_public(False)

        # Private
        response = self.client.get(reverse('profiles:user', args=[self.user1.id]))
        self.assertNotContains(response, 'logs are private')
        self.assertContains(response, 'logs-container')


class EmailChangeTests(TestCase):
    def setUp(self):
        self.user = account_util.create_random_valid_user()

    def test_other_user_email_raises_form_error(self):
        """
        Cannot take the email of another user
        """
        user2 = account_util.create_random_valid_user()

        self.client.force_login(self.user)
        email_form = settings_util.create_email_form(user2.email)
        response = self.client.post(reverse('settings:email'), email_form)
        self.assertContains(response, 'Email already in use')

    def test_same_email_raises_form_error(self):
        """
        Request user's email should also be an invalid email to 'change' into
        """
        self.client.force_login(self.user)
        email_form = settings_util.create_email_form(self.user.email)
        response = self.client.post(reverse('settings:email'), email_form)
        self.assertContains(response, 'Email already in use')

    def test_unused_email_valid_submission(self):
        """
        Valid email form submission should update database properly.
        Old email should no longer work in queries
        """
        self.client.force_login(self.user)
        old_email = self.user.email
        new_email = f'{util.generateRandStr(5)}@{util.generateRandStr(5)}.com'
        email_form = settings_util.create_email_form(new_email)
        self.client.post(reverse('settings:email'), email_form)

        # Assert old email no longer works
        self.assertFalse(CustomUser.objects.filter(email=old_email).exists())
        self.assertEqual(CustomUser.objects.get(email=new_email), self.user)

    def test_input_not_an_email(self):
        """
        Email input must be properly formatted
        """
        self.client.force_login(self.user)
        new_email = f'{util.generateRandStr(100)}'
        email_form = settings_util.create_email_form(new_email)
        response = self.client.post(reverse('settings:email'), email_form)
        self.assertContains(response, 'Enter a valid email address')

class DeleteAccountTests(TestCase):
    def setUp(self):
        self.user = account_util.create_random_valid_user()

    def test_invalid_password_error_message(self):
        """
        If the password entered doesn't match the current user's render an error message
        """
        pass

    def test_valid_password_submission_deletes_account(self):
        """
        Entering the correct password should result in account deletion,
        and redirection to sign up page
        """
        pass


class ChangePasswordTests(TestCase):
    def setUp(self):
        self.uname = account_util.valid_uname
        self.pw = account_util.valid_pass
        self.email = account_util.valid_email
        self.user = account_util.create_user(self.uname, self.pw, email=self.email)

    def test_invalid_pass_confirmation_message(self):
        """
        Invalid password / confirmation should render an message indicating as such
        """
        pass

    def test_invalid_pass_length_message(self):
        """
        Password field should render a message indicating invalid password length
        if it is too short
        """
        pass

    def test_valid_password_change(self):
        """
        Password should change if both input fields match exactly
        """
        pass
