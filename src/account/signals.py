from django.db.models.signals import post_save
from django.dispatch import receiver

from account.models import Referral
from account.tasks import expire_referral


@receiver(post_save, sender=Referral)
def update_stock(sender, instance: Referral, created, **kwargs):
    if created:
        expire_referral.apply_async((instance.id,), eta=instance.expiration_date)

    Referral.objects.exclude(pk=instance.pk).filter(user=instance.user).update(is_active=False)
