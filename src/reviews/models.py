from django.db import models
from django.utils.translation import ugettext_lazy as _

from accounts.models import User
from documents.constants import BOOLEANS
from documents.fields import (
    LeaderCommentsFileField, ApproverCommentsFileField
)


class ReviewMixin(models.Model):
    """A Mixin to use to define reviewable document types."""
    review_start_date = models.DateField(
        _('Review start date'),
        null=True, blank=True
    )
    review_due_date = models.DateField(
        _('Review due date'),
        null=True, blank=True
    )
    under_review = models.NullBooleanField(
        verbose_name=u"Under Review",
        choices=BOOLEANS,
        null=True, blank=True)
    overdue = models.NullBooleanField(
        _('Overdue'),
        choices=BOOLEANS,
        null=True, blank=True)
    reviewers = models.ManyToManyField(
        User,
        verbose_name=_('Reviewers'),
        null=True, blank=True)
    leader = models.ForeignKey(
        User,
        verbose_name=_('Leader'),
        related_name='%(app_label)s_%(class)s_related_leader',
        null=True, blank=True)
    leader_comments = LeaderCommentsFileField(
        _('Leader comments'),
        null=True, blank=True)
    approver = models.ForeignKey(
        User,
        verbose_name=_('Approver'),
        related_name='%(app_label)s_%(class)s_related_approver',
        null=True, blank=True)
    approver_comments = ApproverCommentsFileField(
        _('Approver comments'),
        null=True, blank=True)

    class Meta:
        abstract = True

    def can_be_reviewed(self):
        """Is this revision ready to be reviewed.

        A revision can only be reviewed if all roles have been filled
        (leader, approver and at least one reviewer).

        Also, a revision can only be reviewed once.

        """
        return all((
            self.leader,
            self.approver,
            self.reviewers.count(),
            not self.review_start_date
        ))