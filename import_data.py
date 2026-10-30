# import_data.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'areaPro.settings')
django.setup()

from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command

print("🧹 Clearing content type conflicts...")
ContentType.objects.all().delete()

print("🚀 Loading your local data dump into Render...")
try:
    call_command('loaddata', 'datadump.json')
    print("✅ Success! Your data has been copied to PostgreSQL.")
except Exception as e:
    print(f"❌ Error loading data: {e}")
