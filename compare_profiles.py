from argparse import ArgumentParser
from json import dumps, JSONEncoder, load


class SetEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return JSONEncoder.default(self, obj)


def _get_args():
    # TODO: improve descriptions?
    parser = ArgumentParser('Compare two Apple Sandbox profiles')
    parser.add_argument('-o', '--original', dest='orig', type=str,
        required=True,
        help='the original .sbpl file containing the Sandbox profile')
    parser.add_argument('-d', '--decompiled', dest='dec', type=str,
        required=True,
        help='the decompiled file of Sandbox profile')
    parser.add_argument('-r', '--regex', dest='regex', action='store_true',
        help='compare regular expressions as automata instead of as strings')

    return parser.parse_args()


def _read_graph_file(filename):
    with open(filename) as f:
        graph = {}
        for op, rules in load(f).items():
            graph[op] = set(frozenset(map(
                lambda r: tuple(map(tuple, r)),
                rules
            )))
        return graph


def read_original_file(filename):
    # TODO: use sandbox_compiler.py
    return _read_graph_file(filename)


def read_decompiled_file(filename):
    # TODO: use reverse_sandbox.py
    return _read_graph_file(filename)


def _print_missing_path(sign, path):
    print(f'{sign} {{')
    for node in path:
        print(f'{sign}\t{node}')
    print(f'{sign} }}')


def _print_missing_op(sign, op, paths):
    type = 'Missing' if sign == '-' else 'Erroneous'
    print(f'{sign * 3} {op}:')
    for path in paths:
        _print_missing_path(sign, path)


def _iterate_paths(sign, prev_err, op, paths1, paths2):
    errors = False

    for path1 in paths1:
        og_len = len(path1)
        path_ok = False

        for path2 in paths2:
            if og_len != len(path2):
                continue

            nodes_found = 0
            for node in path1:
                # TODO: compare regexes
                if node in path2:
                    nodes_found += 1
            
            if nodes_found == og_len:
                path_ok = True    
                break
        
        if not path_ok:
            errors = True
            if not prev_err:
                print(f'{op}:')
            _print_missing_path(sign, path1)
    
    return errors


def compare(original, decompiled):	
    for op, paths in original.items():
        if op not in decompiled:
            _print_missing_op('-', op, paths)
            continue

        err = _iterate_paths('-', False, op, paths, decompiled[op])
        _iterate_paths('+', err, op, decompiled[op], paths)
    
    for op in decompiled:
        if op not in original:
            _print_missing_op('+', op, paths)
                

def main(args):
    orig = read_original_file(args.orig)
    dec = read_original_file(args.dec)

    compare(orig, dec)


if __name__ == "__main__":
    args = _get_args()
    main(args)
