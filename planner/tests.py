
from django.test import TestCase
from django.urls import reverse


class SolarWiseTests(TestCase):

    def test_home_page_loads(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)

    def test_signup_page_loads(self):
        response = self.client.get(reverse("signup"))

        self.assertEqual(response.status_code, 200)

    def test_battery_calculator_requires_login(self):
        response = self.client.get(
            reverse("battery_calculator")
        )

        self.assertEqual(response.status_code, 302)
