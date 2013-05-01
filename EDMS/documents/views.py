from django import http
from django.http import HttpResponse, Http404
from django.core.servers.basehttp import FileWrapper
from django.views.generic import (
    View, ListView, CreateView, DetailView, UpdateView
)
from django.utils import simplejson as json
from django.core.urlresolvers import reverse

from documents.models import Document, DocumentRevision
from documents.utils import filter_documents, compress_documents
from documents.forms import (
    DocumentFilterForm, DocumentForm, DocumentDownloadForm,
    DocumentRevisionForm
)
from documents.constants import (
    STATUSES, REVISIONS, UNITS, DISCIPLINES, DOCUMENT_TYPES, CLASSES
)


class JSONResponseMixin(object):
    """Source:
    https://docs.djangoproject.com/en/dev/topics/class-based-views/mixins/
    """
    def render_to_response(self, context):
        """Returns a JSON response containing 'context' as payload"""
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        """Construct an `HttpResponse` object."""
        return http.HttpResponse(content,
                                 content_type='application/json',
                                 **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        """Convert the `document_list` into a JSON object.

        Using DataTables conventions for fields' names.
        """
        documents = context['object_list']
        start = int(self.request.GET.get('iDisplayStart', 1))
        end = start + int(self.request.GET.get('iDisplayLength', 10))
        result = {
            "sEcho": self.request.GET.get("sEcho"),
            "iTotalRecords": Document.objects.all().count(),
            "iTotalDisplayRecords": len(documents),
            "aaData": [doc.jsonified() for doc in documents[start:end]]
        }
        return json.dumps(result)


class DocumentList(ListView):
    # We just need one document to set table's header
    queryset = Document.objects.all()[:1]

    def get_context_data(self, **kwargs):
        context = super(DocumentList, self).get_context_data(**kwargs)
        # Add choices to populate <select>s filters
        context.update({
            'status_choices': [item[0] for item in STATUSES],
            'revisions_choices': [item[0] for item in REVISIONS],
            'units_choices': [item[0] for item in UNITS],
            'disciplines_choices': [item[0] for item in DISCIPLINES],
            'document_types_choices': [item[0] for item in DOCUMENT_TYPES],
            'classes_choices': [item[0] for item in CLASSES],
            'download_form': DocumentDownloadForm()
        })
        return context


class DocumentDetail(DetailView):
    model = Document
    slug_url_kwarg = 'document_number'
    slug_field = 'document_number'

    def get_context_data(self, **kwargs):
        context = super(DocumentDetail, self).get_context_data(**kwargs)
        document = context['document']
        # Attach a form for each revision linked to the current document
        revisions = document.documentrevision_set.all()
        for revision in revisions:
            revision.form = DocumentRevisionForm(instance=revision)
        # Add the form to the context to be rendered in a disabled way
        context.update({
            'is_detail': True,
            'form': DocumentForm(instance=document),
            'revisions': revisions,
        })
        return context


class DocumentFilter(JSONResponseMixin, ListView):
    model = Document

    def get_queryset(self):
        """Given DataTables' GET parameters, filter the initial queryset."""
        queryset = Document.objects.all()
        if self.request.method == "GET":
            form = DocumentFilterForm(self.request.GET)
            if form.is_valid():
                queryset = filter_documents(queryset, form.cleaned_data)

        return queryset


class DocumentRevisionMixin(object):
    """
    Deal with revisions' auto-creation on model creation/edition.
    """
    def form_valid(self, form):
        self.object = form.save()
        # Deal with the new revision if any
        data = form.cleaned_data
        current_revision = data['current_revision']
        if not DocumentRevision.objects.filter(
            revision=current_revision,
            document=self.object
        ).exists():
            DocumentRevision.objects.create(
                document=self.object,
                revision=current_revision,
                revision_date=data['current_revision_date'],
                native_file=data['native_file'],
                pdf_file=data['pdf_file'],
            )
        return http.HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        """Redirect to a different URL given the button clicked by the user."""
        if "save-create" in self.request.POST:
            url = reverse('document_create')
        else:
            url = self.object.get_absolute_url()
        return url


class DocumentCreate(DocumentRevisionMixin, CreateView):
    model = Document
    form_class = DocumentForm


class DocumentEdit(DocumentRevisionMixin, UpdateView):
    model = Document
    form_class = DocumentForm
    slug_url_kwarg = 'document_number'
    slug_field = 'document_number'

    def get_context_data(self, **kwargs):
        context = super(DocumentEdit, self).get_context_data(**kwargs)
        # Add a context var to make the difference with creation view
        context.update({
            'is_edit': True,
        })
        return context

    def get_success_url(self):
        """Redirect to a different URL given the button clicked by the user."""
        if "save-view" in self.request.POST:
            url = self.object.get_absolute_url()
        else:
            url = reverse('document_list')
        return url


class DocumentDownload(View):

    def get(self, request, *args, **kwargs):
        # Deals with GET parameters
        form = DocumentDownloadForm(self.request.GET)
        if form.is_valid():
            data = form.cleaned_data
        else:
            raise Http404('Invalid parameters to download files.')

        # Generates the temporary zip file
        zip_filename = compress_documents(
            data['document_numbers'],
            data['format'] or 'both',
            data['revisions'] or 'latest',
        )
        wrapper = FileWrapper(zip_filename)

        # Returns the zip file for download
        response = HttpResponse(wrapper, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=download.zip'
        response['Content-Length'] = zip_filename.tell()
        zip_filename.seek(0)
        return response