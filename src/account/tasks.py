from account.models import Referral
from config.celery import app


@app.task
def expire_referral(referral_id: int):
    referral = Referral.objects.get(id=referral_id)
    referral.is_active = False
    referral.save(update_fields=['is_active'])
