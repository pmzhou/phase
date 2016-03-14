# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class Activity(models.Model):

    VERB_CREATED = 'created'
    VERB_UPDATED = 'updated'
    VERB_DELETED = 'deleted'
    VERB_JOINED = 'joined'

    VERB_CHOICES = (
        (VERB_CREATED, _("created")),
        (VERB_UPDATED, _("updated")),
        (VERB_DELETED, _("deleted")),
        (VERB_JOINED, _("joined Phase")),
    )

    SYSTEM_USER = _("System")
    NON_DB_USERS = (SYSTEM_USER,)

    # The object that performed the activity.
    actor_content_type = models.ForeignKey(
        ContentType, related_name='actor', blank=True, null=True)
    actor_object_id = models.PositiveIntegerField(blank=True, null=True)
    actor = GenericForeignKey('actor_content_type', 'actor_object_id')
    actor_object_str = models.CharField(
        verbose_name=_("Actor identifier"),
        max_length=254,
        blank=True,
        null=True)

    verb = models.CharField(
        _("Verb"), choices=VERB_CHOICES, default=VERB_JOINED, max_length=128)

    # The object linked to the action itself.
    action_object_content_type = models.ForeignKey(
        ContentType,
        related_name='action_object',
        blank=True,
        null=True)
    action_object_object_id = models.PositiveIntegerField(
        blank=True, null=True)
    action_object = GenericForeignKey(
        'action_object_content_type', 'action_object_object_id')
    action_object_str = models.CharField(max_length=255, blank=True)

    # The object to which the activity was performed.
    target_content_type = models.ForeignKey(
        ContentType, related_name='target', blank=True, null=True)
    target_object_id = models.PositiveIntegerField(blank=True, null=True)
    target = GenericForeignKey(
        'target_content_type', 'target_object_id')
    target_object_str = models.CharField(max_length=255, blank=True)

    created_on = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'audit_trail'
        verbose_name = _('Activity')
        verbose_name_plural = _('Activities')
        ordering = ['-created_on']

    def __unicode__(self):
        ctx = {
            'actor': self.actor or self.actor_object_str,
            'verb': self.get_verb_display(),
            'action_object': self.action_object or self.action_object_str,
            'target': self.target or self.target_object_str,
            'created_on': self.created_on,
        }
        if self.action_object and self.target:
            return _('{actor} {verb} {action_object} on {target} at '
                     '{created_on}').format(**ctx)
        elif self.action_object:
            return _('{actor} {verb} {action_object} at{created_on}').format(**ctx)
        elif self.target:
            return _('{actor} {verb} {target} at {created_on}').format(**ctx)
        return _('{actor} {verb} at {created_on}').format(**ctx)
