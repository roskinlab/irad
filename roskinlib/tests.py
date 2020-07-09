from Bio import Seq
from itertools import count

from .utils import slice_from_range

def test_parse_alignment_structure(record):
    record_name = record['name']
    for parse_label, parse in record['parses'].items():
        if parse is not None:
            query_alignment, alignments = parse['alignments'][0], parse['alignments'][1:]
            assert query_alignment['type'] == 'Q'

            query_length = len(query_alignment['alignment'])

            for alignment, number in zip(alignments, count(1)):
                alignment_type = alignment['type']
                alignment_string = alignment['alignment']
                alignment_length = len(alignment_string)

                padding_start = alignment['padding']['start']
                padding_stop  = alignment['padding']['stop']
                if padding_start + len(alignment_string) + padding_stop != query_length:
                    print(f'record {record_name}, parse {parse_label}, type {alignment_type}{number}:',
                          f'alignments have different length, {padding_start} + {alignment_length} + {padding_stop} != {query_length}')
                    return False

    return True

def calc_germline_diff(query, diff):
    return ''.join(d if d != '.' else q for q, d in zip(query, diff.upper()))

def test_parse_alignment_sequences(record, v_repertoire, d_repertoire, j_repertoire):
    record_name = record['name']
    input_sequence = record['sequence']['sequence']
    for parse_label, parse in record['parses'].items():
        if parse is not None:
            query_alignment, alignments = parse['alignments'][0], parse['alignments'][1:]
            query_string = query_alignment['alignment']
            assert query_alignment['type'] == 'Q'

            query_range = slice_from_range(query_alignment['range'])
            input_substring = input_sequence[query_range]
            if input_substring != query_string.replace('-', ''):
                print(f'record {record_name}, parse {parse_label}, type Q0:',
                        f'query substring does not match query, {input_substring} != {query_string}')
                return False

            for alignment, number in zip(alignments, count(1)):
                alignment_name = alignment['name']
                alignment_type = alignment['type']
                alignment_string = alignment['alignment']
                alignment_query = query_string[alignment['padding']['start']:alignment['padding']['start'] + len(alignment_string)]
                assert len(alignment_string) == len(alignment_query)

                alignment_range = slice_from_range(alignment['range'])
                predicted_germline = calc_germline_diff(alignment_query, alignment_string)
                if alignment_type == 'V':
                    actual_germline = v_repertoire[alignment_name][alignment_range].upper()
                elif alignment_type == 'D':
                    full_germline = d_repertoire[alignment_name].upper()

                    if alignment_range.start is None:
                        alignment_range = slice(0, alignment_range.stop)

                    if alignment_range.stop is None:
                        alignment_range = slice(alignment_range.start, len(d_repertoire[alignment_name]))
                    elif alignment_range.stop < 0:
                        alignment_range = slice(alignment_range.start, len(d_repertoire[alignment_name]) + alignment_range.stop)

                    if alignment_range.start > alignment_range.stop:
                        alignment_range = slice(alignment_range.stop - 1, alignment_range.start + 1)
                        actual_germline = d_repertoire[alignment_name][alignment_range].upper()
                        actual_germline = str(Seq.Seq(actual_germline).reverse_complement())
                    else:
                        actual_germline = d_repertoire[alignment_name][alignment_range].upper()
                elif alignment_type == 'J':
                    actual_germline = j_repertoire[alignment_name][alignment_range].upper()
                else:
                    assert False

                if predicted_germline.replace('-', '') != actual_germline:
                    print(f'record {record_name}, parse {parse_label}, type {alignment_type}{number}:',
                          f'predicted germline does not match germline, {predicted_germline} != {actual_germline}')
                    return False
    
    return True
