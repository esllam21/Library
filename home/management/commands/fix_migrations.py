from django.core.management.base import BaseCommand
from django.db import connections
from django.core.management import call_command
from django.apps import apps
import os


class Command(BaseCommand):
    help = 'Fix migration state by creating a fake migration that matches the current DB state'

    def handle(self, *args, **options):
        self.stdout.write("Step 1: Setting up migration state...")
        
        app_config = apps.get_app_config('home')
        migrations_dir = os.path.join(app_config.path, 'migrations')
        migrations = [f for f in os.listdir(migrations_dir) 
                     if f.endswith('.py') and not f.startswith('__')]
        migrations.sort()
        
        if migrations:
            latest_migration = migrations[-1].replace('.py', '')
            self.stdout.write(f"Latest migration found: {latest_migration}")
            
            self.stdout.write("Marking all migrations as applied...")
            call_command('migrate', 'home', latest_migration, '--fake')
            
            self.stdout.write("Step 2: Creating a new migration that represents the current state...")
            call_command('makemigrations', 'home', '--empty', '--name', 'sync_with_current_db_state')
            
            self.stdout.write(self.style.SUCCESS(
                "Migration state fixed. You may need to manually edit the new migration to add:"
                "\n\n# This is an empty migration that matches the current state of the database."
                "\n# No changes are actually made by this migration."
                "\n\nAnd set operations = [] if it's not already empty."
            ))
        else:
            self.stdout.write(self.style.ERROR("No migrations found for the 'home' app."))
