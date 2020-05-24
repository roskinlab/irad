#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import logging
import time
import os
import io
from itertools import zip_longest

from Bio import SeqIO
import xlsxwriter

from roskinlib.utils import open_compressed


feature_whitelist = set([
    ('CDS', 'experiment'),
    ('CDS', 'function'),
    ('CDS', 'note'),
    ('CDS', 'product'),
    ('C_region', 'gene'),
    ('C_region', 'note'),
    ('C_region', 'product'),
    ('mat_peptide', 'product'),
    ('misc_feature', 'note'),
    ('mRNA', 'product'),
    ('source', 'bio_material'),
    ('source', 'cell_line'),
    ('source', 'cell_type'),
    ('source', 'clone'),
    ('source', 'clone_lib'),
    ('source', 'dev_stage'),
    ('source', 'isolate'),
    ('source', 'isolation_source'),
    ('source', 'lab_host'),
    ('source', 'mol_type'),
    ('source', 'note'),
    ('source', 'serotype'),
    ('source', 'sex'),
    ('source', 'specimen_voucher'),
    ('source', 'sub_clone'),
    ('source', 'tissue_lib'),
    ('source', 'tissue_type')
])

def get_features(record):
    source_features = []
    other_features  = []
    for feature in record.features:
        for key, value in feature.qualifiers.items():
            if (feature.type, key) in feature_whitelist:
                if feature.type == 'source':
                    source_features.append('%s=%s' % (key, '|'.join(value)))
                else:
                    other_features.append('%s:%s=%s' % (feature.type, key, '|'.join(value)))
            if feature.type == 'CDS' and key == 'db_xref':
                for v in value:
                    if v.startswith('HSSP:') or v.startswith('PDB:'):
                        other_features.append('%s:%s=%s' % (feature.type, key, v))

    return source_features, other_features

def equal_references(refs1, refs2):
    for r1, r2 in zip_longest(refs1, refs2):
        if r1.authors != r2.authors:
            return False
        if r1.title != r2.title:
            return False
        if r1.journal != r2.journal:
            # allow 2 mismatches for the journal entry
            mismatch_count = 0
            for c1, c2, in zip_longest(r1.journal, r2.journal):
                if c1 != c2:
                    mismatch_count += 1
                    if mismatch_count > 2:
                        return False
    return True

def get_master_references(records):
    references = None
    for record in records:
        if references is None:
            references = record.annotations['references']
        else:
            assert equal_references(references, record.annotations['references'])

    return references

def write_references(workbook, worksheet, references, current_row=0):
    reference_count = 1
    for r in references:
        worksheet.write_string(current_row, 0, 'Reference ' + str(reference_count))
        worksheet.write_string(current_row, 1, 'Authors')
        worksheet.write_string(current_row, 2, r.authors)

        current_row += 1
        worksheet.write_string(current_row, 1, 'Title')
        worksheet.write_string(current_row, 2, r.title)

        current_row += 1
        worksheet.write_string(current_row, 1, 'Journal')
        worksheet.write_string(current_row, 2, r.journal)

        if r.pubmed_id != '':
            current_row += 1
            worksheet.write_string(current_row, 1, 'PMID')
            worksheet.write_url(current_row, 2, 'https://www.ncbi.nlm.nih.gov/pubmed/' + r.pubmed_id, string=r.pubmed_id)

        current_row += 1
        reference_count += 1

    worksheet.set_column(0, 0, 10.0)
    worksheet.set_column(1, 3, 18.0)

    return current_row

def write_curation_row(workbook, worksheet, records, current_row=0):
    format_bold_dark = workbook.add_format({'bold': True, 'bg_color': '#CCCCCC'})
    format_bold_light = workbook.add_format({'bold': True, 'bg_color': '#EEEEEE'})

    header_row = current_row
    current_row += 1

    # Genbank Features
    worksheet.write_string(current_row,  0, 'Accession', format_bold_dark)
    worksheet.write_string(current_row,  1, 'Description', format_bold_dark)
    worksheet.write_string(current_row,  2, 'Source Features', format_bold_dark)
    worksheet.write_string(current_row,  3, 'Other Features', format_bold_dark)
    # Subject Features
    worksheet.write_string(current_row,  4, 'Age', format_bold_light)
    worksheet.write_string(current_row,  5, 'Sex', format_bold_light)
    worksheet.write_string(current_row,  6, 'Race', format_bold_light)
    worksheet.write_string(current_row,  7, 'Ethnicity', format_bold_light)
    worksheet.write_string(current_row,  8, 'Genotype', format_bold_light)
    # Sample Features
    worksheet.write_string(current_row,  9, 'Disease', format_bold_dark)
    worksheet.write_string(current_row, 10, 'Time Point', format_bold_dark)
    worksheet.write_string(current_row, 11, 'Intervention', format_bold_dark)
    # Cell Origin
    worksheet.write_string(current_row, 12, 'Tissue', format_bold_light)
    worksheet.write_string(current_row, 13, 'Isolation\nMethod', format_bold_light)
    worksheet.write_string(current_row, 14, 'Cell Type', format_bold_light)
    worksheet.write_string(current_row, 15, 'Cell Type\nAssayed', format_bold_light)
    worksheet.write_string(current_row, 16, 'Immortalized', format_bold_light)
    # Sequence Method
    worksheet.write_string(current_row, 17, 'Template', format_bold_dark)
    worksheet.write_string(current_row, 18, 'Amp.\nMethod', format_bold_dark)
    worksheet.write_string(current_row, 19, 'Seq.\n Method', format_bold_dark)
    # Antibody Features
    worksheet.write_string(current_row, 20, 'Isotype', format_bold_light)
    worksheet.write_string(current_row, 21, 'Isotype\nAssayed', format_bold_light)
    worksheet.write_string(current_row, 22, 'Specificity', format_bold_light)
    worksheet.write_string(current_row, 23, 'Specificity\nAssayed', format_bold_light)
    worksheet.write_string(current_row, 24, 'Autoantibody', format_bold_light)
    worksheet.write_string(current_row, 25, 'Binding\nAffinity', format_bold_light)

    current_row += 1

    worksheet.freeze_panes(current_row, 30)

    format_dark = workbook.add_format({'bg_color': '#CCCCCC'})
    format_light = workbook.add_format({'bg_color': '#EEEEEE'})

    for record in records:
        # output the name with URL
        name = record.name
        worksheet.write_url(current_row, 0, 'https://www.ncbi.nlm.nih.gov/nuccore/' + name, string=name, cell_format=format_dark)

        # clean up and write description
        description = record.description
        if description.startswith('Homo sapiens '):
            description = description[len('Homo sapiens '):]
        worksheet.write_string(current_row, 1, description, format_dark)

        # output features about the source and other features
        source_features, other_features = get_features(record)
        worksheet.write_string(current_row, 2, '\n'.join(source_features), format_dark)
        worksheet.write_string(current_row, 3, '\n'.join(other_features), format_dark)

        # color code the groups of columns
        worksheet.write(current_row,  4, '', format_light)
        worksheet.write(current_row,  5, '', format_light)
        worksheet.write(current_row,  6, '', format_light)
        worksheet.write(current_row,  7, '', format_light)
        worksheet.write(current_row,  8, '', format_light)

        worksheet.write(current_row,  9, '', format_dark)
        worksheet.write(current_row, 10, '', format_dark)
        worksheet.write(current_row, 11, '', format_dark)

        worksheet.write(current_row, 12, '', format_light)
        worksheet.write(current_row, 13, '', format_light)
        worksheet.write(current_row, 14, '', format_light)
        worksheet.write(current_row, 15, '', format_light)
        worksheet.write(current_row, 16, '', format_light)

        worksheet.write(current_row, 17, '', format_dark)
        worksheet.write(current_row, 18, '', format_dark)
        worksheet.write(current_row, 19, '', format_dark)

        worksheet.write(current_row, 20, '', format_light)
        worksheet.write(current_row, 21, '', format_light)
        worksheet.write(current_row, 22, '', format_light)
        worksheet.write(current_row, 23, '', format_light)
        worksheet.write(current_row, 24, '', format_light)
        worksheet.write(current_row, 25, '', format_light)

        worksheet.set_row(current_row, 60)

        current_row += 1

    # set the header formatting
    format_merge_dark = workbook.add_format({'bold': True, 'center_across': True, 'bg_color': '#CCCCCC'})
    format_merge_light = workbook.add_format({'bold': True, 'center_across': True, 'bg_color': '#EEEEEE'})
    worksheet.merge_range(header_row,  0, header_row,  3, 'Genbank Features',  format_merge_dark)
    worksheet.merge_range(header_row,  4, header_row,  8, 'Subject Features',  format_merge_light)
    worksheet.merge_range(header_row,  9, header_row, 11, 'Sample Features',   format_merge_dark)
    worksheet.merge_range(header_row, 12, header_row, 16, 'Cell Origin',       format_merge_light)
    worksheet.merge_range(header_row, 17, header_row, 19, 'Sequence Method',   format_merge_dark)
    worksheet.merge_range(header_row, 20, header_row, 25, 'Antibody Features', format_merge_light)
    worksheet.set_row(header_row + 1, 30)

    worksheet.set_column( 4,  6,  5.5)
    worksheet.set_column( 7,  9,  9.5)
    worksheet.set_column(10, 11, 12.5)
    worksheet.set_column(12, 12,  9.5)
    worksheet.set_column(13, 15, 10.5)
    worksheet.set_column(16, 16, 13.5)
    worksheet.set_column(17, 25, 10.5)


    return current_row

def write_genbank_records(workbook, worksheet, records, current_row=0):

    for record in records:
        genbank_string = io.StringIO()

        SeqIO.write(record, genbank_string, 'genbank')

        worksheet.write_string(current_row, 0, genbank_string.getvalue())
        worksheet.set_row(current_row, 500)

        current_row += 1

    format_small_wrap = workbook.add_format({'font_size': 8, 'text_wrap': True})
    worksheet.set_column(0, 0, 65, format_small_wrap)

    return current_row

def main():
    parser = argparse.ArgumentParser(description='generate a sheet for Genbank immune receptor annotation',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # input file
    parser.add_argument('genbank_filename', metavar='genbank-file', help='the file with the Genbank records')

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    start_time = time.time()

    data = {}
    record_counts = 0

    excel_filename = args.genbank_filename
    if '.' in excel_filename:
        excel_filename = excel_filename[:excel_filename.rindex('.')]
    excel_filename += '.xlsx'
    
    # read in the Genbank records
    with open_compressed(args.genbank_filename, 'rt') as genbank_handle:
        # load all the records
        records = list(SeqIO.parse(genbank_handle, 'genbank'))

        # get a unique references list for all records
        references = get_master_references(records)

        # create the workbook
        workbook = xlsxwriter.Workbook(excel_filename)
        curation_worksheet = workbook.add_worksheet('Curation')
        records_worksheet = workbook.add_worksheet('Records')

        # write the references to the sheet
        current_row = write_references(workbook, curation_worksheet, references)

        current_row += 1

        # write curation annotation
        current_row = write_curation_row(workbook, curation_worksheet, records, current_row)

        #
        write_genbank_records(workbook, records_worksheet, records)

        workbook.close()

    elapsed_time = time.time() - start_time
    logging.info('elapsed time %s', time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(elapsed_time)))
    
if __name__ == '__main__':
    sys.exit(main())
