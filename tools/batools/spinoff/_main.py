# Released under the MIT License. See LICENSE for details.
#
"""Spinoff system for spawning child projects from a ballistica project."""

from __future__ import annotations

import os
import sys
import subprocess
from enum import Enum
from typing import assert_never

from efro.error import CleanError
from efro.terminal import Clr
from efrotools import replace_exact
import batools.spinoff
from batools.spinoff._context import SpinoffContext


class Command(Enum):
    """Our top level commands."""

    STATUS = 'status'
    UPDATE = 'update'
    CHECK = 'check'
    CLEAN_LIST = 'cleanlist'
    CLEAN = 'clean'
    CLEAN_CHECK = 'cleancheck'
    OVERRIDE = 'override'
    DIFF = 'diff'
    BACKPORT = 'backport'
    FEATURESETS = 'featuresets'
    CREATE = 'create'


def spinoff_main() -> None:
    """Main script entry point."""
    try:
        _main()
    except CleanError as exc:
        exc.pretty_print()
        sys.exit(1)


def _main() -> None:
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
    if len(sys.argv) < 2:
        print(f'{Clr.RED}Error: Expected a command argument.{Clr.RST}')
        _print_available_commands()
        raise CleanError()

    try:
        cmd = Command(sys.argv[1])
    except ValueError:
        print(f"{Clr.RED}Error: Invalid command '{sys.argv[1]}'.{Clr.RST}")
        _print_available_commands()
        return

    dst_root = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..'))

    # Determine our src project based on our tools/spinoff symlink.
    # If its not a link it means we ARE a src project.
    dst_spinoff_path = os.path.join(dst_root, 'tools', 'spinoff')
    if os.path.islink(dst_spinoff_path):
        src_root = os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.realpath(dst_spinoff_path)), '..'
            )
        )
    else:
        src_root = None

    # By default we assume our src project is a git submodule at
    # submodules/ballistica, but this can be overridden to an arbitrary
    # directory via the project localconfig.
    # src_proj_val = getlocalconfig(Path(dst_root)).get('spinoff_src')
    # if isinstance(src_proj_val, str):
    #     src_root = src_proj_val
    # else:
    #     src_root = os.path.join(dst_root, 'submodules', 'ballistica')

    single_run_mode: SpinoffContext.Mode | None = None

    if cmd is Command.STATUS:
        single_run_mode = SpinoffContext.Mode.STATUS
    elif cmd is Command.UPDATE:
        single_run_mode = SpinoffContext.Mode.UPDATE
    elif cmd is Command.CHECK:
        single_run_mode = SpinoffContext.Mode.CHECK
    elif cmd is Command.CLEAN_LIST:
        single_run_mode = SpinoffContext.Mode.CLEAN_LIST
    elif cmd is Command.CLEAN:
        single_run_mode = SpinoffContext.Mode.CLEAN
    elif cmd is Command.CLEAN_CHECK:
        single_run_mode = SpinoffContext.Mode.CLEAN_CHECK
    elif cmd is Command.DIFF:
        single_run_mode = SpinoffContext.Mode.DIFF
    elif cmd is Command.OVERRIDE:
        _do_override(src_root, dst_root)
    elif cmd is Command.BACKPORT:
        _do_backport(src_root, dst_root)
    elif cmd is Command.FEATURESETS:
        _do_featuresets(dst_root)
    elif cmd is Command.CREATE:
        _do_create(src_root, dst_root)
    else:
        assert_never(cmd)

    if single_run_mode is not None:
        if src_root is None:
            if '--soft' in sys.argv:
                return
            raise CleanError(
                'This only works on dst projects;'
                ' you appear to be in a src project.'
                " To silently no-op in this case, pass '--soft'."
            )
        # SpinoffContext should never be relying on relative paths, so let's
        # keep ourself honest by making sure.
        os.chdir('/')
        SpinoffContext(
            src_root,
            dst_root,
            single_run_mode,
            force='--force' in sys.argv,
            verbose='--verbose' in sys.argv,
            print_full_lists='--full' in sys.argv,
        ).run()


def _do_create(src_root: str | None, dst_root: str) -> None:
    from efrotools.code import format_python_str

    if src_root is not None:
        raise CleanError('This only works on src projects.')

    args = sys.argv[2:]
    args2: list[str] = []
    i = 0

    featuresets: set[str] | None = None

    while i < len(args):
        if args[i] == '--featuresets':
            if i >= len(args) - 1:
                raise CleanError('--featuresets must be followed by an arg.')
            fsarg = args[i + 1]
            if fsarg in {'', 'none'}:
                featuresets = set()
            else:
                featuresets = set(fsarg.split(','))
            i += 2
        else:
            args2.append(args[i])
            i += 1

    if len(args2) != 2:
        raise CleanError(f'Expected a name and path arg; got {args2}.')

    name, path = args2  # pylint: disable=unbalanced-tuple-unpacking

    if not name:
        raise CleanError('Name cannot be an empty string.')
    if not name[0].isupper():
        raise CleanError('Name must start with a capital letter.')

    if os.path.exists(path):
        raise CleanError(f"Target path '{path}' already exists.")

    # The components we need for a spinoff dst project are:
    # - a tools/spinoff symlink pointing to our src project's tools/spinoff
    # - a config/spinoffconfig.py

    subprocess.run(['mkdir', '-p', path], check=True)
    subprocess.run(['mkdir', os.path.join(path, 'tools')], check=True)
    subprocess.run(['mkdir', os.path.join(path, 'config')], check=True)

    subprocess.run(
        [
            'ln',
            '-s',
            os.path.join(dst_root, 'tools', 'spinoff'),
            os.path.join(path, 'tools'),
        ],
        check=True,
    )

    # Read in the dummy module we use as a template.
    template_path = os.path.join(
        os.path.dirname(batools.spinoff.__file__), '_config_template.py'
    )
    with open(template_path, encoding='utf-8') as infile:
        template = infile.read()
    template = replace_exact(
        template,
        '\n# A TEMPLATE CONFIG FOR CREATED SPINOFF DST PROJECTS.\n'
        '# THIS IS NOT USED AT RUNTIME;'
        ' IT ONLY EXISTS FOR TYPE-CHECKING PURPOSES.\n',
        '',
    )
    template = replace_exact(template, 'SPINOFF_TEMPLATE_NAME', name)

    template = replace_exact(
        template,
        '# __SRC_FEATURE_SETS__',
        format_python_str(f'ctx.src_feature_sets = {featuresets!r}'),
    )

    with open(
        os.path.join(path, 'config', 'spinoffconfig.py'), 'w', encoding='utf-8'
    ) as outfile:
        outfile.write(template)

    print(
        f'{Clr.GRN}{Clr.BLD}Spinoff dst project created at'
        f' {Clr.RST}{Clr.BLD}{path}{Clr.RST}{Clr.GRN}.{Clr.RST}\n\n'
        'Next, from dst project root, do:\n'
        f'  {Clr.BLD}{Clr.MAG}./tools/spinoff update{Clr.RST}     '
        '- Syncs src project into dst.\n'
        f'  {Clr.BLD}{Clr.MAG}make update-check{Clr.RST}          '
        '- Makes sure all project files are up-to-date (they should be).\n'
        '  At that point you should have a functional dst project.\n'
    )


def _do_featuresets(dst_root: str) -> None:
    from batools.featureset import FeatureSet

    featuresets = FeatureSet.get_all_for_project(dst_root)
    print(
        f'{Clr.BLD}{len(featuresets)}'
        f' feature-sets present in this project:{Clr.RST}'
    )
    for fset in featuresets:
        print(f'  {Clr.BLU}{fset.name}{Clr.RST}')


def _do_override(src_root: str | None, dst_root: str) -> None:
    if src_root is None:
        raise CleanError('This only works on dst projects.')
    override_paths = [os.path.abspath(p) for p in sys.argv[2:]]
    if not override_paths:
        raise RuntimeError('Expected at least one path arg.')

    # SpinoffContext should never be relying on relative paths, so let's
    # keep ourself honest by making sure.
    os.chdir('/')

    # Do an initial update to make sure everything in the project is kosher.
    # We expect to have a full set of src/dst entities/etc.
    print(f'{Clr.BLU}Bringing project up-to-date before override...{Clr.RST}')
    SpinoffContext(src_root, dst_root, SpinoffContext.Mode.UPDATE).run()

    # Now, in another pass, add filters to the spinoff config to ignore
    # the overridden files and also purge them from the spinoff dst
    # state cache so that they don't get blown away the next time we run
    # spinoff update.
    print(f'{Clr.BLU}Adding overrides...{Clr.RST}')
    SpinoffContext(
        src_root,
        dst_root,
        SpinoffContext.Mode.OVERRIDE,
        override_paths=override_paths,
    ).run()

    # Do one more update which will actually update our spinoff-managed dirs
    # (and related things such as .gitignore) based on the changes we made in
    # the OVERRIDE mode run.
    print(f'{Clr.BLU}Updating state for config changes...{Clr.RST}')
    SpinoffContext(src_root, dst_root, SpinoffContext.Mode.UPDATE).run()


def _do_backport(src_root: str | None, dst_root: str) -> None:
    if src_root is None:
        raise CleanError('This only works on dst projects.')
    args = sys.argv[2:]
    auto = '--auto' in args
    args = [a for a in args if a != '--auto']

    if len(args) not in {0, 1}:
        raise CleanError('Expected zero or one file arg.')

    # None means 'backport first thing in list'.
    backport_file = args[0] if args else None

    # SpinoffContext should never be relying on relative paths, so let's
    # keep ourself honest by making sure.
    os.chdir('/')
    try:
        SpinoffContext(
            src_root,
            dst_root,
            SpinoffContext.Mode.BACKPORT,
            backport_file=backport_file,
            auto_backport=auto,
        ).run()
    except SpinoffContext.BackportInProgressError:
        # We expect this to break us out of processing during backports.
        pass


def _print_available_commands() -> None:
    bgn = Clr.SBLU
    end = Clr.RST
    print(
        (
            'Available commands:\n'
            f'  {bgn}status{end}              '
            'Print list of files update would affect.\n'
            f'  {bgn}diff{end}                '
            'Print diffs for what update would do.\n'
            f'  {bgn}update{end}              '
            'Sync all spinoff files from src project.\n'
            f'  {bgn}check{end}               '
            'Make sure everything is kosher.\n'
            f'  {bgn}clean{end}               '
            'Remove all spinoff files'
            ' (minus a few such as .gitignore).\n'
            f'  {bgn}cleanlist{end}           '
            'Shows what clean would do.\n'
            f'  {bgn}override [file...]{end}  '
            'Remove files from spinoff, leaving local copies in place.\n'
            f'  {bgn}backport [file]{end}     '
            'Help get changes to spinoff dst files back to src.\n'
            f'  {bgn}featuresets{end}         '
            'List featuresets present in the current project.\n'
            f'  {bgn}create [name, path]{end} '
            'Create a new spinoff project based on this src one.\n'
            '                      Name should be in CamelCase form.\n'
            '                      Use --featuresets a,b to specify included'
            ' feature-sets.\n'
            "                      Pass 'none' or an empty string for no"
            ' featuresets.\n'
            '                      If unspecified, all src feature-sets will be'
            ' included.'
        ),
        file=sys.stderr,
    )
