# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import generics

from restapi.views import CategoryAPIViewMixin
from reviews.models import DistributionList
from reviews.api.serializers import DistributionListSerializer


class DistributionListList(CategoryAPIViewMixin, generics.ListAPIView):
    model = DistributionList
    serializer_class = DistributionListSerializer

    def get_queryset(self):
        qs = DistributionList.objects.filter(category=self.get_category())
        return qs
