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
                if padding_start + alignment_length + padding_stop != query_length:
                    print(f'record {record_name}, parse {parse_label}, type {alignment_type}{number}:',
                          f'alignments have different length, {padding_start} + {alignment_length} + {padding_stop} != {query_length}')
                    return False

    return True

def calc_germline_diff(query, diff):
    assert len(query) == len(diff)
    return ''.join(q if d == '.' else d for q, d in zip(query, diff.upper()))

def gapped_equal(s1, s2):
    if len(s1) != len(s2):
        return False

    for b1, b2 in zip(s1, s2):
        if b1 != '.' and b2 != '.':
            if b1 != b2:
                return False

    return True

def test_parse_alignment_sequences(record, v_repertoire, d_repertoire, j_repertoire, remove_caps=False):
    passed_test = True
    record_name = record['name']
    input_sequence = record['sequence']['sequence']
    for parse_label, parse in record['parses'].items():
        if parse is not None:
            query_alignment, alignments = parse['alignments'][0], parse['alignments'][1:]
            query_string = query_alignment['alignment']
            assert query_alignment['type'] == 'Q'
            if query_alignment['padding']['start'] != 0 or query_alignment['padding']['stop'] != 0:
                print(f'record {record_name}, parse {parse_label}, type Q0:',
                        f"query padding ({query_alignment['padding']['start']}, {query_alignment['padding']['stop']}) is not zero")
                passed_test = False

            query_range = slice_from_range(query_alignment['range'])
            input_substring = input_sequence[query_range]
            if remove_caps:
                input_substring = input_substring.replace('A', '').replace('C', '').replace('G', '').replace('T', '')
            if input_substring != query_string.replace('-', '').replace('.', ''):
                print(f'record {record_name}, parse {parse_label}, type Q0:',
                        f'query substring does not match query, {input_substring} != {query_string}')
                passed_test = False

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
                        print(record_name)
                        alignment_range = slice(alignment_range.stop - 1, alignment_range.start + 1)
                        actual_germline = d_repertoire[alignment_name][alignment_range].upper()
                        actual_germline = str(Seq.Seq(actual_germline).reverse_complement())
                    else:
                        actual_germline = d_repertoire[alignment_name][alignment_range].upper()
                elif alignment_type == 'J':
                    actual_germline = j_repertoire[alignment_name][alignment_range].upper()
                else:
                    assert False

                #if predicted_germline.replace('-', '').replace('.', '') != actual_germline:
                if not gapped_equal(predicted_germline.replace('-', ''), actual_germline):
                    print(f'record {record_name}, parse {parse_label}, type {alignment_type}{number}:',
                          f'predicted germline does not match germline, {predicted_germline} != {actual_germline}')
                    passed_test = False

    return passed_test
