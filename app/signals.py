from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PersonPrison

@receiver(post_save, sender=PersonPrison)
def update_current_prison(sender, instance, **kwargs):
    PersonPrison.objects.filter(current=True).filter(person=instance.person).exclude(id=instance.id).update(current=False)
