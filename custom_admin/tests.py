from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from Handyman.models import Category, Review, ServiceProvider


class CustomAdminAccountTests(TestCase):
	def setUp(self):
		self.admin = get_user_model().objects.create_superuser(
			username="paneladmin",
			email="paneladmin@example.com",
			password="StrongAdminPass!814",
		)

	def test_superuser_can_create_another_superuser(self):
		self.client.force_login(self.admin)
		response = self.client.post(
			reverse("directory_admin_add_user"),
			{
				"username": "secondadmin",
				"email": "secondadmin@example.com",
				"password1": "AnotherStrongPass!814",
				"password2": "AnotherStrongPass!814",
				"is_staff": "on",
				"is_superuser": "on",
			},
		)

		self.assertRedirects(response, reverse("directory_admin_users"))
		user = get_user_model().objects.get(username="secondadmin")
		self.assertTrue(user.is_staff)
		self.assertTrue(user.is_superuser)

	def test_non_superuser_cannot_view_user_management(self):
		user = get_user_model().objects.create_user(
			username="regularuser",
			password="RegularUserPass!814",
		)
		self.client.force_login(user)

		response = self.client.get(reverse("directory_admin_users"))

		self.assertEqual(response.status_code, 302)
		self.assertIn("/login/", response["Location"])

	def test_superuser_can_edit_and_toggle_an_account(self):
		user = get_user_model().objects.create_user(
			username="editableuser",
			password="EditableUserPass!814",
		)
		self.client.force_login(self.admin)

		edit_response = self.client.post(
			reverse("directory_admin_edit_user", args=[user.pk]),
			{
				"username": "editableuser",
				"email": "updated@example.com",
				"is_active": "on",
				"is_staff": "on",
			},
		)
		self.assertRedirects(edit_response, reverse("directory_admin_users"))
		user.refresh_from_db()
		self.assertEqual(user.email, "updated@example.com")
		self.assertTrue(user.is_staff)

		toggle_url = reverse("directory_admin_toggle_user_active", args=[user.pk])
		self.client.post(toggle_url)
		user.refresh_from_db()
		self.assertFalse(user.is_active)
		self.client.post(toggle_url)
		user.refresh_from_db()
		self.assertTrue(user.is_active)

	def test_user_cannot_remove_their_own_superuser_access(self):
		self.client.force_login(self.admin)
		self.assertEqual(reverse("directory_admin_dashboard"), "/secure-control-hub/dashboard/")
		self.assertEqual(self.client.get(reverse("directory_admin_dashboard")).status_code, 200)

		response = self.client.post(
			reverse("directory_admin_edit_user", args=[self.admin.pk]),
			{
				"username": self.admin.username,
				"email": self.admin.email,
				"is_active": "on",
				"is_staff": "on",
			},
		)

		self.assertEqual(response.status_code, 200)
		self.admin.refresh_from_db()
		self.assertTrue(self.admin.is_superuser)

	def test_superuser_can_delete_another_user_but_not_themselves(self):
		user = get_user_model().objects.create_user(
			username="deleteuser",
			password="DeleteUserPass!814",
		)
		self.client.force_login(self.admin)

		confirmation = self.client.get(
			reverse("directory_admin_delete_user", args=[user.pk])
		)
		self.assertEqual(confirmation.status_code, 200)
		self.client.post(reverse("directory_admin_delete_user", args=[user.pk]))
		self.assertFalse(get_user_model().objects.filter(pk=user.pk).exists())

		self.client.post(reverse("directory_admin_delete_user", args=[self.admin.pk]))
		self.assertTrue(get_user_model().objects.filter(pk=self.admin.pk).exists())


class CustomAdminMutationMethodTests(TestCase):
	def setUp(self):
		self.admin = get_user_model().objects.create_superuser(
			username="mutationadmin",
			email="mutationadmin@example.com",
			password="StrongAdminPass!814",
		)
		self.category = Category.objects.create(name="Repairs", slug="repairs")
		self.provider = ServiceProvider.objects.create(
			name="Test Repairs",
			category=self.category,
			description="Test listing",
			address="1 Test Street",
			city="Lagos",
			state="Lagos",
			phone="08012345678",
		)
		self.review = Review.objects.create(
			provider=self.provider,
			user=self.admin,
			rating=5,
			comment="Test review",
		)
		self.client.force_login(self.admin)

	def test_get_requests_cannot_mutate_admin_records(self):
		mutation_urls = (
			reverse("custom_admin_approve_provider", args=[self.provider.pk]),
			reverse("delete_provider", args=[self.provider.pk]),
			reverse("delete_category", args=[self.category.pk]),
			reverse("toggle_review_visibility", args=[self.review.pk]),
		)

		for url in mutation_urls:
			with self.subTest(url=url):
				self.assertEqual(self.client.get(url).status_code, 405)

		self.provider.refresh_from_db()
		self.assertEqual(self.provider.status, "pending")
		self.assertTrue(ServiceProvider.objects.filter(pk=self.provider.pk).exists())
		self.assertTrue(Category.objects.filter(pk=self.category.pk).exists())

	def test_superuser_can_toggle_review_visibility(self):
		response = self.client.post(
			reverse("toggle_review_visibility", args=[self.review.pk])
		)
		self.assertRedirects(response, reverse("directory_admin_dashboard"))
		self.review.refresh_from_db()
		self.assertTrue(self.review.is_hidden)

	def test_legacy_moderation_actions_are_post_only(self):
		for action_name in ("approve_provider", "reject_provider"):
			with self.subTest(action=action_name):
				response = self.client.get(reverse(action_name, args=[self.provider.pk]))
				self.assertEqual(response.status_code, 405)

		self.provider.refresh_from_db()
		self.assertEqual(self.provider.status, "pending")

	def test_regular_user_cannot_open_legacy_review_queue(self):
		user = get_user_model().objects.create_user(
			username="regularmoderator",
			password="RegularUserPass!814",
		)
		self.client.force_login(user)

		response = self.client.get(reverse("admin_review_queue"))

		self.assertEqual(response.status_code, 302)
		self.assertIn("/login/", response["Location"])


class CustomAdminCategoryDescriptionTests(TestCase):
	def setUp(self):
		self.admin = get_user_model().objects.create_superuser(
			username="categoryadmin",
			email="categoryadmin@example.com",
			password="StrongAdminPass!814",
		)
		self.client.force_login(self.admin)

	def test_superuser_can_create_and_edit_category_description(self):
		response = self.client.post(
			reverse("add_category"),
			{
				"name": "Home Repairs",
				"description": "Repairs and maintenance for the home.",
				"slug": "home-repairs",
			},
		)

		self.assertRedirects(response, reverse("directory_admin_dashboard"))
		category = Category.objects.get(slug="home-repairs")
		self.assertEqual(category.description, "Repairs and maintenance for the home.")
		self.assertContains(
			self.client.get(reverse("directory_admin_dashboard")),
			"Repairs and maintenance for the home.",
		)

		response = self.client.post(
			reverse("edit_category", args=[category.pk]),
			{
				"name": "Home Repairs",
				"description": "Skilled home repair professionals.",
				"slug": "home-repairs",
			},
		)

		self.assertRedirects(response, reverse("directory_admin_dashboard"))
		category.refresh_from_db()
		self.assertEqual(category.description, "Skilled home repair professionals.")
