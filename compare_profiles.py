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
    parser.add_argument('--ops', dest='ops', type=str,
        help='a file containing the sandbox operations in the decompiled '
            'profile')
    parser.add_argument('-r', '--release', type=str,
        help='a file containing the sandbox operations in the '
            'decompiled profile')
    parser.add_argument('-p', '--profile', type=str,
        help='the name of the profile to compare, in case of a profile bundle')
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


def read_json_graph(filename):
    return _reformat_graph(load(open(filename)))


def read_original_file(filename):
    return _reformat_graph(parse_file(filename))


def read_decompiled_file(filename, ops, release, sbpl, profile):
    if sbpl:
        return read_original_file(filename)
    return _reformat_graph(get_graph_for_profile(filename, ops, release,
        profile))


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
    correct_paths = 0

    for path1 in paths1:
        og_len = len(path1)
        path_ok = False

        for path2 in paths2:
            if og_len != len(path2):
                continue

            if path1 == path2:
                correct_paths += 1
                path_ok = True
                break

        if not path_ok:
            errors = True
            if not prev_err:
                print(f'{operation}:')
                prev_err = True
            _print_missing_path(sign, path1)

    return errors, correct_paths, len(paths1)


def compare(compiled, decompiled):
    errors = False

    total_dec_paths = 0
    total_cpl_paths = 0

    correct_dec_paths = 0
    correct_cpl_paths = 0

    correct_dec_op = 0
    correct_cpl_op = 0

    for oper, paths in compiled.items():
        if oper not in decompiled:
            _print_missing_op('-', oper, paths)
            continue
        correct_cpl_op += 1

        err, correct, total = _iterate_paths('-', False, oper, paths,
            decompiled[oper])
        errors = errors or err
        total_cpl_paths += total
        correct_cpl_paths += correct

        err, correct, total = _iterate_paths('+', err, oper, decompiled[oper], paths)
        errors = errors or err
        total_dec_paths += total
        correct_dec_paths += correct

    for oper, paths in decompiled.items():
        if oper not in compiled:
            errors = True
            _print_missing_op('+', oper, paths)
        else:
            correct_dec_op += 1

    if total_dec_paths:
        print(f'\nCorrect paths in decompiled graph: {correct_dec_paths}/{total_dec_paths}: {correct_dec_paths / total_dec_paths * 100}%')
    else:
        print(f'\nCorrect paths in decompiled graph: {correct_dec_paths}/{total_dec_paths}')
    if total_cpl_paths:
        print(f'Correct paths in compiled graph: {correct_cpl_paths}/{total_cpl_paths}: {correct_cpl_paths / total_cpl_paths * 100}%')
    else:
        print(f'Correct paths in compiled graph: {correct_cpl_paths}/{total_cpl_paths}')
    if decompiled:
        print(f'Correct operations in decompiled graph: {correct_dec_op}/{len(decompiled)}: {correct_dec_op / len(decompiled) * 100}%')
    else:
        print(f'Correct operations in decompiled graph: {correct_dec_op}/{len(decompiled)}')
    if compiled:
        print(f'Correct operations in compiled graph: {correct_cpl_op}/{len(compiled)}: {correct_cpl_op / len(compiled) * 100}%')
    else:
        print(f'Correct operations in compiled graph: {correct_cpl_op}/{len(compiled)}')

    return errors


def main():
    args = _get_args()

    orig = read_original_file(args.orig)
    dec = read_decompiled_file(args.dec, args.ops, args.release, args.sbpl_orig,
        args.profile)

    return compare(orig, dec)


if __name__ == "__main__":
    sys.exit(main())
