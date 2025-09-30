from django.test import TestCase, Client


class SmokeTests(TestCase):
	def test_home_redirects_or_loads(self):
		c = Client()
		resp = c.get('/')
		# either redirect to login or render home; just assert it's a valid response
		self.assertIn(resp.status_code, (200, 302))
