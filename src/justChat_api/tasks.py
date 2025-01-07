# justChatBackend/tasks.py
from django.core.mail import EmailMessage
from celery import shared_task

@shared_task(queue='high_priority', priority=0)  # Priority 0 is highest
def send_user_otp(subject, html_content, mail_from, receipient):
    # Handle high priority work
    email = EmailMessage(subject, html_content, mail_from, receipient)
    email.content_subtype = 'html'
    email.send(fail_silently=False)
    return True

@shared_task(queue='medium_priority', priority=5)
def medium_priority_task(data):
    # Handle medium priority work
    return f'Medium priority task done with {data}'

@shared_task(queue='low_priority', priority=9)  # Priority 9 is lowest
def low_priority_task(data):
    # Handle low priority work
    return f'Low priority task done with {data}'