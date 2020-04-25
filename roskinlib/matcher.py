import sys
import logging
from collections import defaultdict

def expanding_circle(center, radius):
    yield center
    for r in range(1, radius + 1):
        yield center + r
        yield center - r

class OffByNMatcher:
    def __init__(self, sequence_dict, max_diff=0, allow_indels=True, allow_collesion=False):
        #  for each sequence
        sequences_by_length = defaultdict(dict)
        for seq, ident in sequence_dict.items():
            # get the set of off-by-ns
            sequences = self.off_by_n(seq, max_diff, allow_indels)
            for s in sequences:
                l = len(s)
                # check to make sure there are no sequence collesions
                if s in sequences_by_length[l] and ident != sequences_by_length[l][s]:
                    if allow_collesion:
                        logging.warning('collesion between ids %s and %s with sequence %s at edit distance %d',
                                ident, sequences_by_length[l][s], s, max_diff)
                    else:
                        logging.error('collesion between ids %s and %s with sequence %s at edit distance %d',
                                ident, sequences_by_length[l][s], s, max_diff)
                        sys.exit(10)
                sequences_by_length[l][s] = ident
        self.sequences_by_length = sequences_by_length

        # list of what sequences lengths to search for first
        search_length_order = []
        # add the lengths from sequence_dict, longest first
        for start_len in sorted(set([len(s) for s in sequence_dict]), reverse=True):
            search_length_order.append(start_len)
        # if length changes are allowed, add those, longest first
        if allow_indels and max_diff > 0:
            for start_len in sorted([len(s) for s in sequence_dict], reverse=True):
                for l in expanding_circle(start_len, max_diff):
                    if l not in search_length_order:
                        search_length_order.append(l)
        self.search_length_order = search_length_order
        print(search_length_order, file=sys.stderr)

        # check to make sure the sequences lengths are all in the order
        assert set(len(s) for l in sequences_by_length for s in sequences_by_length[l]) == set(search_length_order)
        #print(search_length_order)
    def match_length(self, sequence):
        for l in self.search_length_order:
            query = sequence[:l]
            if query in self.sequences_by_length[l]:
                return self.sequences_by_length[l][query], l
        return None, None
    def match(self, sequence):
        self.match_length(sequence)[0]
    def one_offs(self, sequence, allow_indels):
        bases = ['A', 'C', 'G', 'T']
        splits     = [(sequence[:i], sequence[i:]) for i in range(len(sequence) + 1)]
        replaces   = [left + base + right[1:]      for left, right in splits if right for base in bases]
        if allow_indels:
            deletes    = [left + right[1:]             for left, right in splits if right]
            inserts    = [left + base + right          for left, right in splits for base in bases]
            return set(deletes + replaces + inserts)
        else:
            return set(replaces)
    def off_by_n(self, sequence, n, allow_indels):
        sequences = set()
        sequences.add(sequence)
        for i in range(n):
            additional_sequences = set()
            for sequence in sequences:
                additional_sequences.update(self.one_offs(sequence, allow_indels))
            sequences.update(additional_sequences)
        return sequences

class RandomBarcodeTargetMatcher:
    def __init__(self, random_base_count, random_radius, barcode_dict, target_dict, barcode_max_diff=0, target_max_diff=2, allow_collesion=False):
        assert random_radius <= random_base_count
        self.random_base_count = random_base_count
        self.random_radius = random_radius
        self.barcode_matcher = OffByNMatcher(barcode_dict, barcode_max_diff, allow_indels=False, allow_collesion=allow_collesion)
        self.target_matcher = OffByNMatcher(target_dict, target_max_diff, allow_indels=True, allow_collesion=allow_collesion)
    def match(self, sequence):
        for random_end in expanding_circle(self.random_base_count, self.random_radius):
            seq_barcode = sequence[random_end:]
            barcode_match, barcode_size = self.barcode_matcher.match_length(seq_barcode)
            if barcode_match:
                seq_target = seq_barcode[barcode_size:]
                target_match, target_size = self.target_matcher.match_length(seq_target)
                if target_match:
                    return random_end, barcode_match, barcode_size, target_match, target_size
            else:
                for assumed_barcode_size in self.barcode_matcher.search_length_order:
                    seq_target = seq_barcode[assumed_barcode_size:]
                    target_match, target_size = self.target_matcher.match_length(seq_target)
                    if target_match:
                        return random_end, None, assumed_barcode_size, target_match, target_size
        return None
