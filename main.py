from Bio import SeqIO
from mongoengine import connect
from sequence.SequenceDocument import SequenceDocument
from sequence.SequenceStats import count_wild_type, count_distance_distribution, \
    sequence_stats, get_distribution_stats, count_paired_distance_distribution
from excel.res_xls import create_res_xls
from openpyxl import Workbook
import os
connect(host=os.environ.get("MONGO_HOST"))

regionMap = {
    "Ivano-Frankovskaya": "IF",
    "Belgorodskaya oblast', Krasnogvardeysky rayon": "BK",
    "Belgorodskaya oblast', Grayvoronsky rayon": "BG",
    "L'vovskaya oblast', Stryi": "ST",
    "Cherkasskaya": "CH",
    "Khmelnitskaya": "KHM",
}

otherRegionMap = {
    "Donetskaya": "DO",
    "Odesskaya": "OD",
    "Rovenskaya": "RO",
    "Kharkovskaya": "KHA",
    "Zhitomirskaya": "ZH",
    "Sumskaya": "SU",
    "Belgorodskaya oblast' unspecified": "B",
    "undefined: UND": "UND"
}


# def countATGC(sequence):
#     Ac = sequence.count("A")
#     Tc = sequence.count("T")
#     Gc = sequence.count("G")
#     Cc = sequence.count("C")
#     Lc = (Ac + Tc + Gc + Cc)
#     GCc = ((Gc + Cc) / (Ac + Tc + Gc + Cc + 0.0)) * 100
#     ATc = ((Ac + Tc) / (Ac + Tc + Gc + Cc + 0.0)) * 100
#     return Ac, Tc, Gc, Cc, Lc, GCc, ATc


def parce_base_sequence(filePath, file_format):
    for record in SeqIO.parse(filePath, file_format):
        seqId = str(record.id)
        seq = str(record.seq.upper())
        document = SequenceDocument(
            version=seqId,
            length=len(seq),
            fasta=record.format('fasta'),
            sequence=seq,
            name=record.name
        )
        document.save()
        return document.id


def query_base_sequence(name):
    return SequenceDocument.objects(name=name)[0]


def load_all_sequences(filename, file_format):
    for seqRecord in SeqIO.parse(filename, file_format):
        if len(seqRecord.seq) == 377:
            seq = seqRecord.seq.upper()
            location = []
            region = ''
            for feature in seqRecord.features:
                if feature.type == 'source':
                    start = feature.location.nofuzzy_start
                    end = feature.location.nofuzzy_end
                    country = feature.qualifiers.get('country', ['undefined: UND'])
                    location = [start, end]
                    region = country[0]
            # count nucleoid stats if needed
            # reset stats first
            # count_nucleoid_stats(seq)
            document = SequenceDocument(
                version=str(seqRecord.id),
                length=len(seq),
                fasta=seqRecord.format('fasta'),
                sequence=str(seq),
                location=location,
                region=region
            )
            document.save()


def get_sequences_by_region(region):
    return SequenceDocument.objects(region__contains=region).only('sequence')


def create_sheet_with_results(workbook, region, sequences):
    # query rCRS base sequence
    rcrs_base_sequence = query_base_sequence('NC_012920')
    # parse RSRS base sequence
    rsrs_base_sequence = query_base_sequence('RSRS')
    wild_type = count_wild_type()
    wild_type_rcrs_distance = count_distance_distribution([wild_type], rcrs_base_sequence.sequence[16023:16400])[0]
    wild_type_rsrs_distance = count_distance_distribution([wild_type], rsrs_base_sequence.sequence[16023:16400])[0]

    rcrs_distance = count_distance_distribution(sequences, rcrs_base_sequence.sequence[16023:16400])
    rcrs_distance_stats = sequence_stats(rcrs_distance)
    rcrs_histogram, rcrs_histogram_parts = get_distribution_stats(rcrs_distance)

    rsrs_distance = count_distance_distribution(sequences, rsrs_base_sequence.sequence[16023:16400])
    rsrs_distance_stats = sequence_stats(rsrs_distance)
    rsrs_histogram, rsrs_histogram_parts = get_distribution_stats(rsrs_distance)

    wild_type_distance = count_distance_distribution(sequences, wild_type)
    wild_type_distance_stats = sequence_stats(wild_type_distance)
    wild_type_histogram, wild_type_histogram_parts = get_distribution_stats(wild_type_distance)

    paired_distance = count_paired_distance_distribution(sequences)
    paired_distance_stats = sequence_stats(paired_distance)
    paired_histogram, paired_histogram_parts = get_distribution_stats(paired_distance)

    other_stats = [str(wild_type), wild_type_rcrs_distance, wild_type_rsrs_distance, sum(rcrs_distance),
                   sum(rsrs_distance)]
    print(f'rCRS DISTANCE = {rcrs_distance}')
    print(f'rCRS DISTANCE histogram = {rcrs_histogram}')
    print(f'rCRS DISTANCE histogram parted = {rcrs_histogram_parts}')
    print(f'rCRS DISTANCE stats = {rcrs_distance_stats}')

    print(f'RSRS DISTANCE = {rsrs_distance}')
    print(f'RSRS DISTANCE stats = {rsrs_distance_stats}')

    print(f'wild type DISTANCE = {wild_type_distance}')
    print(f'wild type DISTANCE stats = {wild_type_distance_stats}')
    print("======================")

    regionMapped = regionMap.get(region, 'Other Regions')

    create_res_xls(
        workbook=workbook,
        rcrs_distribution=rcrs_histogram,
        rcrs_distribution_percent=rcrs_histogram_parts,
        rcrs_stats=rcrs_distance_stats,
        rsrs_distribution=rsrs_histogram,
        rsrs_distribution_percent=rsrs_histogram_parts,
        rsrs_stats=rsrs_distance_stats,
        wild_type_distribution=wild_type_histogram,
        wild_type_distribution_percent=wild_type_histogram_parts,
        wild_type_stats=wild_type_distance_stats,
        pair_distribution=paired_histogram,
        pair_distribution_percent=paired_histogram_parts,
        pair_stats=paired_distance_stats,
        other_stats=other_stats,
        region=regionMapped
    )


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # parse rCRS base sequence
    # parce_base_sequence("rCRS.gb", "genbank")

    # rsrs_id = parce_base_sequence("RSRS.fasta", "fasta")

    # Initialize position stats documents
    # init_seq_position_stats(377)
    # Load the db
    load_all_sequences("data/sequence.gb", "genbank")
    workbook = Workbook()
    for region in regionMap.keys():
        sequences_obj = get_sequences_by_region(region)
        sequences = [sequence.sequence for sequence in sequences_obj]
        create_sheet_with_results(workbook, region, sequences)

    sequences = []
    for region in otherRegionMap.keys():
        sequences_obj = get_sequences_by_region(region)
        sequences.extend([sequence.sequence for sequence in sequences_obj])
    create_sheet_with_results(workbook, 'Other Regions', sequences)

