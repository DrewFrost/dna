from itertools import combinations
from statistics import mean, mode

from Levenshtein._levenshtein import distance
from numpy import histogram
from scipy.stats import sem, variation

from SequencePositionStats import SequencePositionStats
from Bio.Seq import Seq


def init_seq_position_stats(length=377):
    for i in range(length):
        seq_pos_stats = SequencePositionStats(
            A_count=0,
            T_count=0,
            G_count=0,
            C_count=0,
            position=i
        )
        seq_pos_stats.save()


def reset_seq_position_stats():
    for seq_positions in SequencePositionStats.objects().sort_by('position'):
        seq_positions.update(set__A_count=0)
        seq_positions.update(set__T_count=0)
        seq_positions.update(set__G_count=0)
        seq_positions.update(set__C_count=0)


def update_seq_pos_stats(position, nucleoid):
    if nucleoid == 'A':
        SequencePositionStats.objects(position=position).update(inc__A_count=1)
    elif nucleoid == 'T':
        SequencePositionStats.objects(position=position).update(inc__T_count=1)
    elif nucleoid == 'G':
        SequencePositionStats.objects(position=position).update(inc__G_count=1)
    elif nucleoid == 'C':
        SequencePositionStats.objects(position=position).update(inc__C_count=1)


def count_nucleoid_stats(seq):
    for i in range(len(seq)):
        nucleoid = seq[i]
        print(f'Nucleoid: {nucleoid}, position: {i}')
        update_seq_pos_stats(i, nucleoid)


def count_wild_type():
    wild_sequence = ''
    for seqPositions in SequencePositionStats.objects().order_by('position'):
        maxCounts = max(seqPositions.A_count, seqPositions.T_count, seqPositions.C_count, seqPositions.G_count)
        if maxCounts == seqPositions.A_count:
            wild_sequence += 'A'
        elif maxCounts == seqPositions.T_count:
            wild_sequence += 'T'
        elif maxCounts == seqPositions.G_count:
            wild_sequence += 'G'
        elif maxCounts == seqPositions.C_count:
            wild_sequence += 'C'
    print(wild_sequence)
    return Seq(wild_sequence)


def count_distance_distribution(sequences, base_sequence):
    distances = []
    for sequence in sequences:
        dist = distance(str(sequence), str(base_sequence))
        distances.append(dist)
    return distances


def count_paired_distance_distribution(sequences):
    distances = []
    for sequence1, sequence2 in combinations(sequences, 2):
        dist = distance(str(sequence1), str(sequence2))
        distances.append(dist)
    return distances


def get_distribution_stats(arr):
    hist = histogram(arr)
    hist = hist[0]
    total = sum(hist)
    parted_hist = [i / total for i in hist]
    return hist, parted_hist


def sequence_stats(arr):
    expected_value = mean(arr)
    standard_error = sem(arr)
    distance_mode = mode(arr)
    distance_min = min(arr)
    distance_max = max(arr)
    distance_variation = variation(arr)
    return [expected_value, standard_error, distance_mode, distance_min, distance_max, distance_variation]