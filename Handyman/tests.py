from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Category, Review, ServiceProvider


class AccountPersistenceTests(TestCase):
    def test_signup_logout_and_login_with_same_credentials(self):
        credentials = {
            'username': 'persistent_member',
            'password1': 'LocalConnect!Secure814',
            'password2': 'LocalConnect!Secure814',
        }

        signup_response = self.client.post('/signup/', credentials)
        self.assertEqual(signup_response.status_code, 302)

        user = get_user_model().objects.get(username=credentials['username'])
        self.assertTrue(user.check_password(credentials['password1']))
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

        logout_response = self.client.post('/logout/')
        self.assertRedirects(logout_response, '/')
        self.assertNotIn('_auth_user_id', self.client.session)

        login_response = self.client.post(
            '/login/',
            {
                'username': credentials['username'],
                'password': credentials['password1'],
            },
        )
        self.assertEqual(login_response.status_code, 302)
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)


class ReviewFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='reviewer',
            email='reviewer@example.com',
            password='StrongPass123!',
        )
        self.category = Category.objects.create(
            name='Plumbing',
            slug='plumbing',
        )
        self.provider = ServiceProvider.objects.create(
            name='City Fix',
            category=self.category,
            description='Test provider',
            address='123 Main St',
            city='Lagos',
            state='Lagos',
            neighborhood='Yaba',
            phone='08012345678',
            email='cityfix@example.com',
            is_verified=True,
            status='approved',
            owner=self.user,
        )

    def test_review_creation_works(self):
        review = Review.objects.create(
            provider=self.provider,
            user=self.user,
            rating=5,
            comment='Excellent service.',
        )

        self.assertEqual(review.provider, self.provider)
        self.assertEqual(review.rating, 5)
        self.assertEqual(self.provider.average_rating(), 5.0)


class OwnerDashboardTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='owner',
            email='owner@example.com',
            password='StrongPass123!',
        )
        self.other_user = get_user_model().objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='StrongPass123!',
        )
        self.category = Category.objects.create(
            name='Cleaning',
            slug='cleaning',
        )
        self.provider = ServiceProvider.objects.create(
            name='Spark Clean',
            category=self.category,
            description='Home cleaning services',
            address='9 New Road',
            city='Abuja',
            state='FCT',
            neighborhood='Garki',
            phone='08022222222',
            email='spark@example.com',
            is_verified=False,
            status='pending',
            owner=self.user,
        )

    def test_dashboard_lists_only_current_users_businesses(self):
        self.client.login(username='owner', password='StrongPass123!')
        response = self.client.get('/dashboard/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Spark Clean')

    def test_pending_listings_are_not_visible_on_public_home_page(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Spark Clean')
