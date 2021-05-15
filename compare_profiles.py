from argparse import ArgumentParser
from json import load
import sys

sys.path.append('sandscout/profile_compilation')
from sandscout_compiler import parse_file

sys.path.append('sandblaster/reverse-sandbox')
from reverse_sandbox import get_graph_for_profile


def _get_args():
    parser = ArgumentParser('Compare two Apple Sandbox profiles')
    parser.add_argument('-o', '--original', dest='orig', type=str,
        required=True,
        help='the original .sbpl file containing the Sandbox profile')
    parser.add_argument('-d', '--decompiled', dest='dec', type=str,
        required=True,
        help='the decompiled file of Sandbox profile')
    parser.add_argument('--ops', dest='ops', type=str, required=False,
        help='a file containing the sandbox operations in the decompiled '
            'profile')
    parser.add_argument('-r', '--release', dest='release', type=str,
        required=False, help='a file containing the sandbox operations in the '
            'decompiled profile')
    parser.add_argument('--sbpl', dest='sbpl_orig', action='store_true',
        help='use an SBPL (instead of binary) file for the original profile')
    parser.add_argument('--regex', dest='regex', action='store_true',
        help='compare regular expressions as automata instead of as strings')

    args = parser.parse_args()
    if not args.sbpl_orig and (args.ops is None or args.release is None):
        print('Invalid parameter combination. You must specify either --sbpl, '
            'or both --ops and --release parameteres.\n')
        print(parser.print_help())
        sys.exit(-1)

    return args


def _reformat_graph(old_graph):
    return {
        op: frozenset(frozenset(map(tuple, rules)))
            for op, rules in old_graph.items()
    }


def read_original_file(filename):
    return _reformat_graph(parse_file(filename))


def read_decompiled_file(filename, ops, release, sbpl):
    if sbpl:
        return read_original_file(filename)
    return _reformat_graph(get_graph_for_profile(filename, ops, release))


def _print_missing_path(sign, path):
    print(f'{sign} {{')
    for node in path:
        print(f'{sign}\t{node}')
    print(f'{sign} }}')


def _print_missing_op(sign, operation, paths):
    print(f'{sign * 3} {operation}:')
    for path in paths:
        _print_missing_path(sign, path)


def _iterate_paths(sign, prev_err, operation, paths1, paths2):
    errors = False

    for path1 in paths1:
        og_len = len(path1)
        path_ok = False

        for path2 in paths2:
            if og_len != len(path2):
                continue

            if path1 == path2:
                path_ok = True
                break

        if not path_ok:
            errors = True
            if not prev_err:
                print(f'{operation}:')
                prev_err = True
            _print_missing_path(sign, path1)

    return errors


def compare(original, decompiled):
    errors = False
    for oper, paths in original.items():
        if oper not in decompiled:
            _print_missing_op('-', oper, paths)
            continue

        err = _iterate_paths('-', False, oper, paths, decompiled[oper])
        errors = errors or err

        err = _iterate_paths('+', err, oper, decompiled[oper], paths)
        errors = errors or err

    for oper, paths in decompiled.items():
        if oper not in original:
            errors = True
            _print_missing_op('+', oper, paths)

    return errors


def main():
    args = _get_args()

    orig = read_original_file(args.orig)
    dec = read_decompiled_file(args.dec, args.ops, args.release, args.sbpl_orig)

    return compare(orig, dec)


if __name__ == "__main__":
    sys.exit(main())
