from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def add_user_to_explorer_group(sender, instance, created, **kwargs):
    if created: 
        group, created = Group.objects.get_or_create(name='Explorador') 
        instance.groups.add(group)  
