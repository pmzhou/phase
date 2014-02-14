from django import forms
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class BaseDocumentFilterForm(forms.Form):
    """Base form for filtering documents of any type.

    This base form will be used to build forms to validate data submitted with
    the datatables jquery plugin.

    """
    length = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False,
        initial=settings.PAGINATE_BY)
    start = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False,
        initial=0)
    search_terms = forms.CharField(
        label=u'Search all columns',
        required=False)


def filterform_factory(model):
    """Dynamicaly create a filter form for the given Metadata model.

    Filter fields can be either located in the Metadata class, or in the
    corresponding Revision class.

    """
    revision_model = model.latest_revision.get_queryset().model
    all_fields = dict((field.name, field) for field in (
        model._meta.concrete_fields + revision_model._meta.concrete_fields))

    # Get the list of all configured fields
    config = getattr(model, 'PhaseConfig', None)
    if config is None:
        raise ImproperlyConfigured('Configure your document in a PhaseConfig subclass')
    filter_fields = config.filter_fields

    kwargs = {
        'required': False,
    }

    field_list = []
    for field_name in filter_fields:
        if not field_name in all_fields:
            continue

        f = all_fields[field_name]

        # Create form field from model field
        # TODO Include indexes in choices
        field = f.formfield(**kwargs)
        field.required = False
        field.empty_value = None
        field.initial = ''
        field.choices = f.get_choices(include_blank=True)
        field_list.append((f.name, field))

    field_list = dict(field_list)
    field_list.update({
        'sort_by': forms.CharField(
            widget=forms.HiddenInput(),
            required=False,
            initial=model._meta.ordering[0])
    })
    class_name = model.__name__ + 'FilterForm'
    return type(class_name, (BaseDocumentFilterForm,), dict(field_list))
