import warnings

import pandas as pd

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.simplefilter(action='ignore', category=FutureWarning)


def add_rows(args):
    df = pd.DataFrame(
        columns=[
            'sentence_number_from_instruction',
            'sentence_number_from_external_doc',
            'value',
            'text_of_instruction',
            'instruction_filename',
            'text_of_external_doc',
            'external_doc_filename'
        ])
    rows = args
    for row in rows:
        df = df.append({
            'sentence_number_from_instruction': row['sentence_number_from_instruction'],
            'sentence_number_from_external_doc': row['sentence_number_from_external_doc'],
            'value': row['value'],
            'text_of_instruction': row['text_of_instruction'],
            'instruction_filename': row['instruction_filename'],
            'text_of_external_doc': row['text_of_external_doc'],
            'external_doc_filename': row['external_doc_filename'],
        }, ignore_index=True)
    return df
