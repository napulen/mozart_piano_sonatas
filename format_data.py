"""
How to derive the relational data structure from the (MS3) MSCX files:
On the toplevel of the repo, run
    python extract_annotations.py scores -cnmqos
"""

import argparse, os, sys
from fractions import Fraction as frac
try:
    import pandas as pd
except ImportError:
    sys.exit("""This script requires the pandas package. You can install it using the command
python -m pip install pandas""")


os.environ['NUMEXPR_MAX_THREADS'] = '64' # to silence NumExpr prompt
idx = pd.IndexSlice                      # for easy MultiIndex slicing

LOSTR2INT = lambda l: [] if l == '' else [int(s) for s in l.split(', ')]

CONVERTERS = {
    'act_dur': frac,
    'next': LOSTR2INT,
    'nominal_duration': frac,
    'offset': frac,
    'onset': frac,
    'duration': frac,
    'scalar': frac,}

DTYPES = {
    'barline': str,
    'dont_count': 'Int64',
    'keysig': int,
    'mc': int,
    'midi': int,
    'mn': int,
    'numbering_offset': 'Int64',
    'repeats': str,
    'staff': int,
    'tied': 'Int64',
    'timesig': str,
    'tpc': int,
    'voice': int,
    'voices': int,
    'volta': 'Int64',
}

FILE_LIST = pd.DataFrame({'filename':
  {(1, 1): 'K279-1',
  (1, 2): 'K279-2',
  (1, 3): 'K279-3',
  (2, 1): 'K280-1',
  (2, 2): 'K280-2',
  (2, 3): 'K280-3',
  (3, 1): 'K281-1',
  (3, 2): 'K281-2',
  (3, 3): 'K281-3',
  (4, 1): 'K282-1',
  (4, 2): 'K282-2',
  (4, 3): 'K282-3',
  (5, 1): 'K283-1',
  (5, 2): 'K283-2',
  (5, 3): 'K283-3',
  (6, 1): 'K284-1',
  (6, 2): 'K284-2',
  (6, 3): 'K284-3',
  (7, 1): 'K309-1',
  (7, 2): 'K309-2',
  (7, 3): 'K309-3',
  (8, 1): 'K311-1',
  (8, 2): 'K311-2',
  (8, 3): 'K311-3',
  (9, 1): 'K310-1',
  (9, 2): 'K310-2',
  (9, 3): 'K310-3',
  (10, 1): 'K330-1',
  (10, 2): 'K330-2',
  (10, 3): 'K330-3',
  (11, 1): 'K331-1',
  (11, 2): 'K331-2',
  (11, 3): 'K331-3',
  (12, 1): 'K332-1',
  (12, 2): 'K332-2',
  (12, 3): 'K332-3',
  (13, 1): 'K333-1',
  (13, 2): 'K333-2',
  (13, 3): 'K333-3',
  (14, 1): 'K457-1',
  (14, 2): 'K457-2',
  (14, 3): 'K457-3',
  (15, 1): 'K533-1',
  (15, 2): 'K533-2',
  (15, 3): 'K533-3',
  (16, 1): 'K545-1',
  (16, 2): 'K545-2',
  (16, 3): 'K545-3',
  (17, 1): 'K570-1',
  (17, 2): 'K570-2',
  (17, 3): 'K570-3',
  (18, 1): 'K576-1',
  (18, 2): 'K576-2',
  (18, 3): 'K576-3'}})

FILE_LIST.index.names = ['sonata', 'movement']






def check_dir(d):
    if not os.path.isdir(d):
        d = os.path.join(os.getcwd(),d)
        if not os.path.isdir(d):
            if input(d + ' does not exist. Create? (y|n)') == "y":
                os.mkdir(d)
            else:
                raise argparse.ArgumentTypeError(d + ' needs to be an existing directory')
    if not os.path.isabs(d):
        d = os.path.abspath(d)
    return d



def format_data(name=None, dir=None, unfold=False, sonatas=None, movements=None, test=False, notes=False, harmonies=False, cadences=False, measures=False, join=False, propagate=False):
    fname = ' '.join(sys.argv[1:]) if name is None else name

    if dir is None:
        dir = os.path.join(os.getcwd(), 'formatted')

    selection = select_files(sonatas=sonatas, movements=movements)

    if test:
        print(selection)
    elif not harmonies and not cadences and not notes and not measures:
        print("Select the kind of data: -N for notes, -H for harmony labels, -M for measures, and -C for cadence labels. Pass -j to join several kinds into a single TSV.")
    elif len(selection) == 0:
        print("No data matching your selection.")
    else:
        script_path = os.path.abspath('')
        kinds = []
        for kind in ['notes', 'harmonies', 'cadences']:
            if locals()[kind]:
                kinds.append(kind)
        if join:
            assert len(kinds) > 1, "Select at least two kinds of data for joining."
        if (join or unfold) and not 'measures' in kinds:
            kinds.append('measures')

        print(f"Reading {len(selection) * len(kinds)} TSV files...")
        joining = {kind: read_tsvs(os.path.join(script_path, kind), selection) for kind in kinds}

        if unfold:
            print("Calculating unfolding structures...")
            mn_seq_needed = not join and 'cadences' in kinds
            mc_sequences, mn_sequences = {}, {}
            for file, measure_list in joining['measures'].groupby(level=0):
                ml = measure_list.set_index('mc')
                seq = next2sequence(ml.next)
                mc_sequences[file] = seq
                if mn_seq_needed:
                    mn_seq = ml.mn.loc[seq]
                    mn_sequences[file] = mn_seq[mn_seq != mn_seq.shift()].to_list()

        if join:
            joined = join_tsv(**joining)
            print(joined.index.names)
            if unfold:
                print("Unfolding joined DataFrame...")
                store_result(unfold_multiple(joined, mc_sequences=mc_sequences), fname, 'joined')
            else:
                store_result(joined.drop(columns='volta'), fname, 'joined')
        else:
            for kind, tsv in joining.items():
                if kind != 'measures':
                    if unfold:
                        print(f"Unfolding {kind}...")
                        store_result(unfold_multiple(tsv, mc_sequences=mc_sequences, mn_sequences=mn_sequences), fname, kind)
                    elif 'volta' in tsv.columns:
                        store_result(tsv.drop(index=tsv[tsv.volta.fillna(2) == 1].index, columns='volta'), fname, kind)
                    else:
                        store_result(tsv, fname, kind)

        if measures:
            tsv = joining['measures']
            tsv.next = tsv.next.map(lambda l: ', '.join(str(s) for s in l))
            store_result(tsv, fname, 'measures')

        # if propagate:
        #     if cadences:
        #         joined.cadence.fillna(method='bfill', inplace=True)
        #     if notes and harmonies:
        #         joined.chords.fillna(method='ffill', inplace=True)



def join_tsv(notes=None, harmonies=None, cadences=None, measures=None):
    """"""
    if notes is not None:
        if harmonies is not None:
            print("Joining notes with harmony labels...")
            left = pd.merge(notes.set_index(['mc', 'mn', 'onset'], append=True), harmonies.set_index(['mc', 'mn', 'onset'], append=True), left_index=True, right_index=True, how='outer', sort=True, suffixes=('', '_y'))
            duplicates = [col for col in left.columns if col.endswith('_y')]
            left = left.reset_index(level='mc').drop(columns=duplicates)
        else:
            left = notes.set_index(['mn', 'onset'], append=True)
    else:
        left = harmonies.set_index(['mn', 'onset'], append=True)

    if cadences is not None:
        print("Adjoining cadence labels...")
        res = pd.merge(left, cadences.set_index(['mn', 'onset'], append=True), left_index=True, right_index=True, how='outer', sort=True)
    else:
        res = left
    if res.mc.isna().any():
        res.loc[res.mc.isna(), 'mc'] = pd.merge(res[res.mc.isna()].reset_index(level='onset')['onset'], measures[['mc', 'mn']], on=['filename', 'mn']).set_index(['mn', 'onset'], append=True)
    return res.reset_index(['mn', 'onset'])



def next2sequence(nxt):
    """Turns a pd.Series of lists into a sequence of elements."""
    i = nxt.index[0]
    last_i = nxt.index[-1]
    acc = [i]
    nxt = nxt.to_dict()
    flag = 0
    nxt_list = nxt[i]
    l = len(nxt_list)
    while i <= last_i:
        if i == last_i:
            if flag or l == 0:
                break
            elif l == 1: # last mc has repeat sign
                i = nxt_list[0]
                flag = 1
            else:
                raise NotImplementedError
        elif l == 1:
            i = nxt_list[0]
        elif l == 2:
            i = nxt_list[flag]
            flag = int(not flag)
        else:
            raise NotImplementedError("More than two voltas.")
        acc.append(i)
        nxt_list = nxt[i]
        l = len(nxt_list)
    return acc



def read_tsvs(dir, selection):
    files = (selection.filename + '.tsv').values
    df = pd.concat([pd.read_csv(os.path.join(dir, f), sep='\t', dtype=DTYPES, converters=CONVERTERS) for f in files],
                     keys=selection.filename,)
    return df.droplevel(1)



def select_files(sonatas=None, movements=None):
    """

    """
    if sonatas is None:
        df = FILE_LIST
    else:
        df = FILE_LIST.loc[sonatas]
    if movements is not None:
        df = df.loc[idx[:, movements],]
    return df



def store_result(df, fname, what):
    tsv_name = f"{fname}_{what}.tsv" if what != 'joined' else fname + '.tsv'
    tsv_path = os.path.join(args.dir, tsv_name)
    df.to_csv(tsv_path, sep='\t')
    print(f"PREVIEW of {tsv_path}:", df.head(1), sep='\n', end='\n\n')



def unfold_multiple(unfold_this, mc_sequences, mn_sequences=None):

    def unfold(df):
        """
        """
        file = df.iloc[0].name
        if 'mc' in df.columns:
            seq = [mc for mc in mc_sequences[file]  if mc in df.mc.values]
            return df.set_index('mc').loc[seq]
        else:
            seq = [mn for mn in mn_sequences[file]  if mn in df.mn.values]
            return df.set_index('mn').loc[seq]

    res = unfold_this.groupby(level=0).apply(unfold)
    if 'volta' in res.columns:
        res.drop(columns='volta', inplace=True)
    return res.reset_index(level=1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description = '''\
------------------------------------
| Format Mozart data to your needs |
------------------------------------

This script needs to remain at the top level of (your local copy of) the repo  mozart_piano_sonatas.
Run with parameter -t to see all file names.
''')
    parser.add_argument('name', metavar='NAME', nargs='?', type=check_dir, help='You may choose a name for the new TSV file(s). Existing files will be overwritten.')
    parser.add_argument('dir', metavar='DIR', nargs='?', type=check_dir, default=os.path.join(os.getcwd(), 'formatted'), help='Folder for storing the new TSV file(s). Can be relative, defaults to ./formatted')
    parser.add_argument('-u','--unfold', action='store_true', help="Unfold: Repeat everything that is repeated in the score, taking into account first and second endings ('voltas'). Otherwise, only second endings are returned.")
    parser.add_argument('-s','--sonatas', nargs='+', type=int, help="Select sonatas out of 1-18, e.g. -s 2 5 12")
    parser.add_argument('-m','--movements', nargs='+', type=int, help="Select only movements 1, 2 or 3, e.g. -m 1 3")
    parser.add_argument('-t','--test', action='store_true', help="Only test/view file selection without storing any data. Use -t without -sm to view all files.")
    parser.add_argument('-N','--notes', action='store_true', help="Get note lists.")
    parser.add_argument('-H','--harmonies', action='store_true', help="Get harmony labels.")
    parser.add_argument('-C','--cadences', action='store_true', help="Get cadence labels.")
    parser.add_argument('-M','--measures', action='store_true', help="Get measure properties.")
    parser.add_argument('-j','--join', action='store_true', help="Join the data into one single TSV.")
    parser.add_argument('-p','--propagate', action='store_true', help="When joining, spread out chord and cadence labels.")
    args = parser.parse_args()

    format_data(args.name,
                args.dir,
                args.unfold,
                args.sonatas,
                args.movements,
                args.test,
                args.notes,
                args.harmonies,
                args.cadences,
                args.measures,
                args.join,
                args.propagate)
