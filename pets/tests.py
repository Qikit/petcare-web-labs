from django.test import TestCase
from django.urls import reverse

from users.models import User
from pets.models import Pet


class PetAuthzTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='o@test.ru', password='pwd12345')
        self.stranger = User.objects.create_user(email='s@test.ru', password='pwd12345')
        self.pet = Pet.objects.create(
            owner=self.owner, name='Барсик', species='cat', age=24,
        )

    def test_owner_can_edit(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('pet-edit', args=[self.pet.pk]))
        self.assertEqual(response.status_code, 200)

    def test_stranger_gets_404_on_edit(self):
        self.client.force_login(self.stranger)
        response = self.client.get(reverse('pet-edit', args=[self.pet.pk]))
        self.assertEqual(response.status_code, 404)

    def test_stranger_cannot_delete(self):
        self.client.force_login(self.stranger)
        response = self.client.post(reverse('pet-delete', args=[self.pet.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Pet.objects.filter(pk=self.pet.pk).exists())

    def test_anonymous_redirected_to_login(self):
        response = self.client.get(reverse('pet-list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)
