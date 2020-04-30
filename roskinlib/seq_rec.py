def best_vdj_score(parse):
    best_v       = None
    best_v_score = None
    best_d       = None
    best_d_score = None
    best_j       = None
    best_j_score = None

    if parse is not None:
        for a in parse['alignments']:
            if a['type'] == 'V' and best_v_score is None:
                best_v       = a['name']
                best_v_score = a['score']
            elif a['type'] == 'D' and best_d_score is None:
                best_d       = a['name']
                best_d_score = a['score']
            elif a['type'] == 'J' and best_j_score is None:
                best_j       = a['name']
                best_j_score = a['score']

    return best_v, best_v_score, best_d, best_d_score, best_j, best_j_score

def get_parse_query(parse):
    if parse is None:
        return None
    else:
        alignment = parse['alignments'][0]
        assert alignment['type'] == 'Q'
        return alignment['alignment']

def make_slice(range_):
    return slice(range_['start'], range_['stop'])

def get_query_region(parse, region):
    if parse is None:
        return None

    if region not in parse['ranges']:
        return None

    query_sequence = get_parse_query(parse)
    region_slice = make_slice(parse['ranges'][region])

    return query_sequence[region_slice].replace('-', '')

def remove_allele(s):
    return s.split('*')[0]
