#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from allauth.socialaccount.models import SocialApp

apps = SocialApp.objects.filter(provider='google')
print(f'Found {apps.count()} Google Social Apps:')
for app in apps:
    sites = list(app.sites.values_list('domain', flat=True))
    print(f'  ID: {app.id}, Name: {app.name}, Client ID: {app.client_id[:20]}..., Sites: {sites}')

if apps.count() > 1:
    print('\nYou need to delete the duplicate entries. Keep only one.')
    print('You can delete by ID using Django Admin or by running:')
    print('python manage.py shell')
    print('>>> from allauth.socialaccount.models import SocialApp')
    print('>>> SocialApp.objects.get(id=<duplicate_id>).delete()')
