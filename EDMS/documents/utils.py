import zipfile
import tempfile
try:
    import zlib
    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED

from django.db.models import Q

from documents.models import Document


def filter_documents(queryset, data):
    """Filter documents from a queryset given data from DataTables.

    Documentation (lack of is more accurate though):
    http://www.datatables.net/examples/server_side/server_side.html
    """
    # Dummy document to retrieve displayed fields
    # TODO: find a better way to achieve this
    document = Document.objects.latest('document_number')
    display_fields = document.display_fields()
    searchable_fields = document.searchable_fields()

    # Paging (done at the view level, the whole queryset is still required)

    # Ordering
    if 'iSortCol_0' in data:
        sort_column = data['iSortCol_0']
        sort_direction = data['sSortDir_0'] == u'desc' and u'-' or u''
        if sort_column == 0:  # fallback on document_number
            column_name = (sort_direction+'document_number',)
        else:
            column_name = (sort_direction+display_fields[sort_column][1],)
        queryset = queryset.order_by(*column_name)

    # Filtering (global)
    if 'sSearch' in data:
        search_terms = data['sSearch']
        if search_terms:
            q = Q()
            for field in searchable_fields:
                q.add(Q(**{'%s__icontains' % field: search_terms}), Q.OR)
            queryset = queryset.filter(q)

    # Filtering (per field)
    for i, field in enumerate(display_fields):
        if data.get('sSearch_'+str(i-1), False):
            queryset = queryset.filter(**{
                '%s__exact' % field[1]: data['sSearch_'+str(i-1)]
            })

    return queryset


def compress_documents(documents, format='both', revisions='latest'):
    """Compress the given files' documents (or queryset) in a zip file.

    * format can be either 'both', 'native' or 'pdf'
    * revisions can be either 'latest' or 'all'

    Returns the name of the ziped file.
    """
    temp_file = tempfile.TemporaryFile()

    with zipfile.ZipFile(temp_file, mode='w') as zip_file:
        files = []
        for document in documents:
            if revisions == 'latest':
                revs = [document.latest_revision()]
            elif revisions == 'all':
                revs = document.documentrevision_set.all()

            for rev in revs:
                if rev is not None:
                    if format in ('native', 'both'):
                        files.append(rev.native_file)
                    if format in ('pdf', 'both'):
                        files.append(rev.pdf_file)

        for file_ in files:
            zip_file.write(
                file_.path,
                file_.name,
                compress_type=compression
            )
    return temp_file