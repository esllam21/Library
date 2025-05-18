from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
import os


class Command(BaseCommand):
    help = 'Reset migrations completely by creating a fresh initial migration that matches the current DB state'

    def add_arguments(self, parser):
        parser.add_argument(
            '--proceed',
            action='store_true',
            help='Proceed with migration reset without confirmation',
        )

    def handle(self, *args, **options):
        if not options['proceed']:
            self.stdout.write(self.style.WARNING(
                "WARNING: This command will delete all existing migrations and create a fresh initial migration.\n"
                "It should only be used when the migration history is completely out of sync with the database.\n"
                "Make sure you have a backup of your database before proceeding.\n"
                "To continue, run the command with the --proceed flag."
            ))
            return

        app_name = 'home'
        
        self.stdout.write("Step 1: Clearing migration history for 'home' app...")
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM django_migrations WHERE app = %s", [app_name])
        
        self.stdout.write("Step 2: Removing old migration files...")
        migrations_dir = os.path.join('home', 'migrations')
        for filename in os.listdir(migrations_dir):
            if filename != '__init__.py' and filename.endswith('.py'):
                file_path = os.path.join(migrations_dir, filename)
                os.remove(file_path)
                self.stdout.write(f"Removed: {file_path}")
        
        self.stdout.write("Step 3: Creating fresh initial migration...")
        call_command('makemigrations', app_name)
        
        self.stdout.write("Step 4: Fake-applying the new migration...")
        call_command('migrate', app_name, '--fake-initial')
        
        self.stdout.write(self.style.SUCCESS(
            "Migration reset completed successfully. The migration history now reflects your current models."
        ))
