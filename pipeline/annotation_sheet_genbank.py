#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import logging
import time
import os
import io
from itertools import zip_longest
from collections import defaultdict

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
    all_references = set()

    direct_journal_dates = defaultdict(set)
    direct_author = {}
    direct_title = {}

    for record in records:
        for reference in record.annotations['references']:
            if reference.title == 'Direct Submission':
                # trim and extract the date from the "journal"
                journal =  reference.journal
                assert journal.startswith('Submitted (')
                date = journal[journal.index('(') + 1:journal.index(')')]
                journal = journal[journal.index(')') + 1:]

                direct_journal_dates[journal].add(date)
                direct_author[journal] = reference.authors
                direct_title[journal]  = reference.title
            else:
                all_references.add((reference.authors, reference.title, reference.journal, reference.pubmed_id))

    for journal in direct_journal_dates:
        all_references.add((direct_author[journal], direct_title[journal],
                            'Submitted (' + ','.join(direct_journal_dates[journal]) + ')' + journal, ''))

    return all_references

def write_references(workbook, worksheet, references, current_row=0):
    format_dark       = workbook.add_format({'bg_color': '#CCCCCC'})
    format_dark_bold  = workbook.add_format({'bold': True, 'bg_color': '#CCCCCC'})
    format_light      = workbook.add_format({'bg_color': '#EEEEEE'})
    format_light_bold = workbook.add_format({'bold': True, 'bg_color': '#EEEEEE'})


    formats = [format_light, format_dark]
    formats_bold = [format_light_bold, format_dark_bold]

    reference_count = 1
    for authors, title, journal, pubmed_id in references:
        worksheet.write_string(current_row, 0, 'Reference ' + str(reference_count), formats_bold[reference_count % 2])
        worksheet.write_string(current_row, 1, 'Authors', formats_bold[reference_count % 2])
        worksheet.merge_range(current_row,  2, current_row, 27, authors, formats[reference_count % 2])

        current_row += 1
        worksheet.write_string(current_row, 0, '', formats_bold[reference_count % 2])
        worksheet.write_string(current_row, 1, 'Title', formats_bold[reference_count % 2])
        worksheet.merge_range(current_row,  2, current_row, 27, title, formats[reference_count % 2])

        current_row += 1
        worksheet.write_string(current_row, 0, '', formats_bold[reference_count % 2])
        worksheet.write_string(current_row, 1, 'Journal', formats_bold[reference_count % 2])
        worksheet.merge_range(current_row,  2, current_row, 27, journal, formats[reference_count % 2])

        if pubmed_id != '':
            current_row += 1
            worksheet.write_string(current_row, 0, '', formats_bold[reference_count % 2])
            worksheet.write_string(current_row, 1, 'PMID', formats_bold[reference_count % 2])
            worksheet.merge_range(current_row,  2, current_row, 27, None)
            worksheet.write_url(current_row,    2, 'https://www.ncbi.nlm.nih.gov/pubmed/' + pubmed_id,
                    string=pubmed_id, cell_format=formats[reference_count % 2])

        current_row += 1
        reference_count += 1

    worksheet.set_column(0, 0, 12.0)
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
    worksheet.write_string(current_row,  4, 'Subject ID', format_bold_light)
    worksheet.write_string(current_row,  5, 'Age', format_bold_light)
    worksheet.write_string(current_row,  6, 'Sex', format_bold_light)
    worksheet.write_string(current_row,  7, 'Race', format_bold_light)
    worksheet.write_string(current_row,  8, 'Ethnicity', format_bold_light)
    worksheet.write_string(current_row,  9, 'Genotype', format_bold_light)
    # Sample Features
    worksheet.write_string(current_row, 10, 'Sample ID', format_bold_dark)
    worksheet.write_string(current_row, 11, 'Disease', format_bold_dark)
    worksheet.write_string(current_row, 12, 'Time Point', format_bold_dark)
    worksheet.write_string(current_row, 13, 'Intervention', format_bold_dark)
    # Cell Origin
    worksheet.write_string(current_row, 14, 'Tissue', format_bold_light)
    worksheet.write_string(current_row, 15, 'Isolation\nMethod', format_bold_light)
    worksheet.write_string(current_row, 16, 'Cell Type', format_bold_light)
    worksheet.write_string(current_row, 17, 'Cell Type\nAssayed', format_bold_light)
    worksheet.write_string(current_row, 18, 'Immortalized', format_bold_light)
    # Sequence Method
    worksheet.write_string(current_row, 19, 'Template', format_bold_dark)
    worksheet.write_string(current_row, 20, 'Amp.\nMethod', format_bold_dark)
    worksheet.write_string(current_row, 21, 'Seq.\n Method', format_bold_dark)
    # Antibody Features
    worksheet.write_string(current_row, 22, 'Isotype', format_bold_light)
    worksheet.write_string(current_row, 23, 'Isotype\nAssayed', format_bold_light)
    worksheet.write_string(current_row, 24, 'Specificity', format_bold_light)
    worksheet.write_string(current_row, 25, 'Specificity\nAssayed', format_bold_light)
    worksheet.write_string(current_row, 26, 'Binding\nAffinity', format_bold_light)
    worksheet.write_string(current_row, 27, 'Autoantibody', format_bold_light)

    current_row += 1

    worksheet.freeze_panes(current_row, 1)

    format_dark = workbook.add_format({'bg_color': '#CCCCCC'})
    format_dark_wrap = workbook.add_format({'bg_color': '#CCCCCC', 'text_wrap': True})
    format_light = workbook.add_format({'bg_color': '#EEEEEE'})

    for record in records:
        # output the name with URL
        name = record.name
        worksheet.write_url(current_row, 0, 'https://www.ncbi.nlm.nih.gov/nuccore/' + name, string=name, cell_format=format_dark)

        # clean up and write description
        description = record.description
        if description.startswith('Homo sapiens '):
            description = description[len('Homo sapiens '):]
        worksheet.write_string(current_row, 1, description, format_dark_wrap)

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
        worksheet.write(current_row,  9, '', format_light)

        worksheet.write(current_row, 10, '', format_dark)
        worksheet.write(current_row, 11, '', format_dark)
        worksheet.write(current_row, 12, '', format_dark)
        worksheet.write(current_row, 13, '', format_dark)

        worksheet.write(current_row, 14, '', format_light)
        worksheet.write(current_row, 15, '', format_light)
        worksheet.write(current_row, 16, '', format_light)
        worksheet.write(current_row, 17, '', format_light)
        worksheet.write(current_row, 18, '', format_light)

        worksheet.write(current_row, 19, '', format_dark)
        worksheet.write(current_row, 20, '', format_dark)
        worksheet.write(current_row, 21, '', format_dark)

        worksheet.write(current_row, 22, '', format_light)
        worksheet.write(current_row, 23, '', format_light)
        worksheet.write(current_row, 24, '', format_light)
        worksheet.write(current_row, 25, '', format_light)
        worksheet.write(current_row, 26, '', format_light)
        worksheet.write(current_row, 27, '', format_light)

        worksheet.set_row(current_row, 60)

        current_row += 1

    # set the header formatting
    format_merge_dark = workbook.add_format({'bold': True, 'center_across': True, 'bg_color': '#CCCCCC'})
    format_merge_light = workbook.add_format({'bold': True, 'center_across': True, 'bg_color': '#EEEEEE'})
    worksheet.merge_range(header_row,  0, header_row,  3, 'Genbank Features',  format_merge_dark)
    worksheet.merge_range(header_row,  4, header_row,  9, 'Subject Features',  format_merge_light)
    worksheet.merge_range(header_row, 10, header_row, 13, 'Sample Features',   format_merge_dark)
    worksheet.merge_range(header_row, 14, header_row, 18, 'Cell Origin',       format_merge_light)
    worksheet.merge_range(header_row, 19, header_row, 21, 'Sequence Method',   format_merge_dark)
    worksheet.merge_range(header_row, 22, header_row, 27, 'Antibody Features', format_merge_light)
    worksheet.set_row(header_row + 1, 30)

    worksheet.set_column( 4,  4,  9.5)
    worksheet.set_column( 5,  7,  5.5)
    worksheet.set_column( 8, 10,  9.5)
    worksheet.set_column(11, 11, 10.5)
    worksheet.set_column(12, 13, 12.5)
    worksheet.set_column(14, 14,  9.5)
    worksheet.set_column(15, 17, 10.5)
    worksheet.set_column(18, 18, 13.5)
    worksheet.set_column(19, 26, 10.5)
    worksheet.set_column(27, 27, 12.5)

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
