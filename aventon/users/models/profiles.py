from django.db import models
from aventon.utils.models import MetaModel
from django.dispatch import receiver
from django.db.models.signals import post_save

from .users import User


class Profile(MetaModel):
    """
    A profile holds a user's public data like biography, picture, and statistics
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField(
        'profile picture',
        upload_to='users/pictures/',
        blank=True,
        null=True
    )
    biography = models.TextField(max_length=500, blank=True)

    # Stats
    rides_taken = models.PositiveIntegerField(default=0)
    rides_offered = models.PositiveIntegerField(default=0)
    reputation = models.FloatField(
        default=5.0,
        help_text="User's reputation based on the rides taken and offered."
    )

    def __str__(self):
        return str(self.user)


@receiver(post_save, sender=User)
def ensure_profile_exists(sender, instance, **kwargs):
    if kwargs.get('created', False):
        Profile.objects.get_or_create(user=instance)
