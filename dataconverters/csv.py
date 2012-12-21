import json
from messytables import (
    CSVTableSet,
    headers_guess,
    headers_processor,
    offset_processor,
    type_guess,
    StringType,
    IntegerType,
    FloatType,
    DecimalType)
from messytables.types import DateUtilType


def csv_to_json(stream, **kwargs):
    '''Convert CSV file to JSON as per the standard Data Convert API.

    Special arguments supported:

    None at present

    TODO: all CSV args
    '''
    metadata = dict(**kwargs)
    table_set = CSVTableSet.from_fileobj(stream)
    row_set = table_set.tables.pop()
    offset, headers = headers_guess(row_set.sample)

    fields = []
    dup_columns = {}
    noname_count = 1
    header_type = int(metadata.get('header_type', 0))
    if header_type:
        guess_types = [StringType, IntegerType, FloatType, DecimalType, DateUtilType]
        row_types = type_guess(row_set.sample, guess_types)
    for index, field in enumerate(headers):
        field_dict = {}
        if "" == field:
            field = '_'.join(['column', unicode(noname_count)])
            headers[index] = field
            noname_count += 1
        if headers.count(field) == 1:
            field_dict['id'] = field
        else:
            dup_columns[field] = dup_columns.get(field, 0) + 1
            field_dict['id'] = u'_'.join([field, unicode(dup_columns[field])])
        if header_type:
            if isinstance(row_types[index], DateUtilType):
                field_dict['type'] = 'DateTime'
            else:
                field_dict['type'] = str(row_types[index])
        fields.append(field_dict)
    row_set.register_processor(headers_processor([x['id'] for x in fields]))
    row_set.register_processor(offset_processor(offset + 1))

    data_row = {}
    result = []
    for row in row_set:
        for index, cell in enumerate(row):
            data_row[cell.column] = cell.value
        result.append(data_row)
    return fields, result
