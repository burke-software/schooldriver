from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.db.models.signals import post_syncdb
from django.db.models import Q
import ecwsp.work_study.models

def fix_perm_content_type(sender, **kwargs):
    try:
        work_user_content_type = ContentType.objects.get(app_label="work_study",name="work team user")
        auth_content_type = ContentType.objects.filter(app_label="auth",name="user")
        for perm in Permission.objects.filter(content_type=auth_content_type).filter(
            Q(name="Can add work team user")
            | Q(name="Can change work team user")
            | Q(name="Can delete work team user")
            ):
            perm.content_type = work_user_content_type
            try:
                perm.save()
            except: pass # old databases may have this change already and error
    except:
        pass

post_syncdb.connect(fix_perm_content_type, sender=ecwsp.work_study.models)
