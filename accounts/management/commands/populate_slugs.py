from django.core.management.base import BaseCommand
from django.utils.text import slugify
from accounts.models import User


class Command(BaseCommand):
    help = 'Populate the slug field for all users'
    def handle(self, *args, **kwargs):
        users = User.objects.all()
        for user in users:
            if not user.slug:
                # slug_base = f"{user.first_name} {user.last_name}" if user.first_name and user.last_name else user.username
                # slug = slugify(slug_base, allow_unicode=True)
                # unique_slug = slug
                # counter = 1
                # while User.objects.filter(slug=unique_slug).exists():
                #     unique_slug = f"{slug}-{counter}"
                user.save()
               
                self.stdout.write(self.style.SUCCESS(f'Successfully updated slug for user {user.username}'))