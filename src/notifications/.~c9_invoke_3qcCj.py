from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

from .signals import notify
from django.core.urlresolvers import reverse

# Create your models here.
class NotificationQuerySet(models.query.QuerySet):
    def get_user(self, user):
        return self.filter(recipient=user)

    # Not used
    # def mark_targetless(self, recipient):
    #     qs = self.unread().get_user(recipient)
    #     qs_no_target = qs.filter(target_object_id=None)
    #     if qs_no_target:
    #         qs_no_target.update(read=True)

    def mark_all_read(self, recipient):
        qs = self.unread().get_user(recipient)
        qs.update(read=True)

    def mark_all_unread(self, recipient):
        qs = self.read().get_user(recipient)
        qs.update(read=False)

    def unread(self):
        return self.filter(read=False)

    def read(self):
        return self.filter(read=True)

    def recent(self):
        return self.unread()[:5]


class NotificationManager(models.Manager):
    def get_queryset(self):
        return NotificationQuerySet(self.model, using=self._db)

    # not used
    # def all_unread(self, user):
    #     return get_queryset().get_user(user).unread()

    # not used
    # def all_read(self, user):
    #     return get_queryset().get_user(user).read()

    # it could be shorted into one QuerySet line
    def all_for_user(self, user):
        self.get_queryset().mark_targetless(recipient=user)
        return self.get_queryset().get_user(user)

    def get_recent_for_user(self, user):
        return self.get_queryset().get_user(user)[:6]


class Notification(models.Model):
    sender_content_type = models.ForeignKey(ContentType,
                                            related_name='notify_sender')
    sender_object_id = models.PositiveIntegerField()
    sender_object = GenericForeignKey("sender_content_type",
                                      "sender_object_id")
    
    # what it describes what action it does. it useful for debuging
    verb = models.CharField(max_length=255)
    action_content_type = models.ForeignKey(ContentType,
                                            related_name='notify_action',
                                            null=True, blank=True)
    action_object_id = models.PositiveIntegerField(null=True, blank=True)
    action_object = GenericForeignKey("action_content_type",
                                      "action_object_id")

    target_content_type = models.ForeignKey(ContentType,
                                            related_name="notify_target",
                                            null=True, blank=True)
    target_object_id = models.PositiveIntegerField(null=True, blank=True)
    target_object = GenericForeignKey("target_content_type",
                                      "target_object_id")

    # recipient is considered as an instance of MyUser model
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  related_name='notifications')
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

    objects = NotificationManager()

    def __unicode__(self):
        try:
            target_url = self.target_object.get_absolute_url()
        except:
            target_url = None
        context = {
            "sender": self.sender_object,
            "verb": self.verb,
            "action": self.action_object,
            "target": self.target_object,
            # test it out, not sure whether it's working fine or not
            "verify_read": reverse("notifications_read", kwargs={"id":
                                                                 self.id}),
            "target_url": target_url,
        }
        if self.target_object:
            if self.action_object and target_url:
                # http://doha.slyip.com/notifications/read/11/?next=/comment/92/
                return "%(sender)s %(verb)s <a href='%(verify_read)s?next=%(target_url)s'>%(target)s</a> with %(action)s" % context
            if self.action_object and not target_url:
                return "%(sender)s %(verb)s %(target)s with %(action)s" % context

            return "%(sender)s %(verb)s %(target)s" % context
        return "%(sender)s %(verb)s" % context

    @property
    def get_link(self):
        try:
            target_url = self.target_object.get_absolute_url()
        except:
            target_url = reverse("notifications_all")

        context = {
            "sender": self.sender_object,
            "verb": self.verb,
            "action": self.action_object,
            "target": self.target_object,
            "verify_read": reverse("notifications_read", kwargs={"id":
                                                                 self.id}),
            "target_url": target_url,
        }

        if self.target_object:
            return "<a href='%(verify_read)s?next=%(target_url)s'>%(sender)s %(verb)s %(target)s with %(action)s</a>" % context
        else:
            return "<a href='%(verify_read)s?next=%(target_url)s'>%(sender)s %(verb)s</a>" % context


def new_notification(sender, **kwargs):
    print("kwargs", kwargs)
    # new_notification_create = Notification.objects.create(recipient=recipient, action=action)
    recipient = kwargs.pop('recipient')
    verb = kwargs.pop('verb')
    affected_users = kwargs.pop('affected_users', None)
    print "affected_users:", affected_users
    target = kwargs.pop('target', None)
    action = kwargs.pop('action', None)
    
    if affected_users is not None:
        for u in affected_users:
            if u == sender:
                print("a sender user:", u)
                pass
            else:
                print("not a sender users:", u)
                new_note = Notification(recipient=u,
                                        verb=verb,
                                        sender_content_type=ContentType.objects.get_for_model(sender),
                                        sender_object_id=sender.id
                                        )
                if target is not None:
                    new_note.target_content_type = ContentType.objects.get_for_model(target)
                    new_note.target_object_id = target.id
            
                if action is not None:
                    new_note.action_content_type = ContentType.objects.get_for_model(action)
                    new_note.action_object_id = action.id
                    new_note.save()
    else:
        new_note = Notification(recipient=recipient,
                                verb=verb,
                                sender_content_type=ContentType.objects.get_for_model(sender),
                                sender_object_id=sender.id
                                )
        if target is not None:
            new_note.target_content_type = ContentType.objects.get_for_model(target)
            new_note.target_object_id = target.id
    
        if action is not None:
            new_note.action_content_type = ContentType.objects.get_for_model(action)
            new_note.action_object_id = action.id
            new_note.save()
        new_note.save()

notify.connect(new_notification)