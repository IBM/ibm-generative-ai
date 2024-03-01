# This file contains code modified from the 'sphinx-multiversion' project
# Original author: Jan Holthuis
# The original code is licensed under the BSD 2-Clause "Simplified" License.

# -*- coding: utf-8 -*-
import argparse
import contextlib
import itertools
import json
import logging
import multiprocessing
import os
import pathlib
import re
import string
import subprocess
import sys
import tempfile

from sphinx import config as sphinx_config
from sphinx import project as sphinx_project

from . import git, sphinx


@contextlib.contextmanager
def working_dir(path):
    prev_cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)


def load_sphinx_config_worker(q, confpath, confoverrides, add_defaults):
    try:
        with working_dir(confpath):
            current_config = sphinx_config.Config.read(
                confpath,
                confoverrides,
            )

        if add_defaults:
            current_config.add("smv_tag_whitelist", sphinx.DEFAULT_TAG_WHITELIST, "html", str)
            current_config.add(
                "smv_branch_whitelist",
                sphinx.DEFAULT_TAG_WHITELIST,
                "html",
                str,
            )
            current_config.add(
                "smv_remote_whitelist",
                sphinx.DEFAULT_REMOTE_WHITELIST,
                "html",
                str,
            )
            current_config.add(
                "smv_released_pattern",
                sphinx.DEFAULT_RELEASED_PATTERN,
                "html",
                str,
            )
            current_config.add(
                "smv_outputdir_format",
                sphinx.DEFAULT_OUTPUTDIR_FORMAT,
                "html",
                str,
            )
            current_config.add("smv_prefer_remote_refs", False, "html", bool)
            current_config.add("smv_prebuild_command", "", "html", str)
            current_config.add("smv_postbuild_command", "", "html", str)
        current_config.pre_init_values()
        current_config.init_values()
    except Exception as err:
        q.put(err)
        return

    q.put(current_config)


def load_sphinx_config(confpath, confoverrides, add_defaults=False):
    q = multiprocessing.Queue()
    proc = multiprocessing.Process(
        target=load_sphinx_config_worker,
        args=(q, confpath, confoverrides, add_defaults),
    )
    proc.start()
    proc.join()
    result = q.get_nowait()
    if isinstance(result, Exception):
        raise result
    return result


def get_python_flags():
    if sys.flags.bytes_warning:
        yield "-b"
    if sys.flags.debug:
        yield "-d"
    if sys.flags.hash_randomization:
        yield "-R"
    if sys.flags.ignore_environment:
        yield "-E"
    if sys.flags.inspect:
        yield "-i"
    if sys.flags.isolated:
        yield "-I"
    if sys.flags.no_site:
        yield "-S"
    if sys.flags.no_user_site:
        yield "-s"
    if sys.flags.optimize:
        yield "-O"
    if sys.flags.quiet:
        yield "-q"
    if sys.flags.verbose:
        yield "-v"
    for option, value in sys._xoptions.items():
        if value is True:
            yield from ("-X", option)
        else:
            yield from ("-X", "{}={}".format(option, value))


def main(argv=None):
    if not argv:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser()
    parser.add_argument("sourcedir", help="path to documentation source files")
    parser.add_argument("outputdir", help="path to output directory")
    parser.add_argument(
        "filenames",
        nargs="*",
        help="a list of specific files to rebuild. Ignored if -a is specified",
    )
    parser.add_argument(
        "-c",
        metavar="PATH",
        dest="confdir",
        help=("path where configuration file (conf.py) is located " "(default: same as SOURCEDIR)"),
    )
    parser.add_argument(
        "-C",
        action="store_true",
        dest="noconfig",
        help="use no config file at all, only -D options",
    )
    parser.add_argument(
        "-D",
        metavar="setting=value",
        action="append",
        dest="define",
        default=[],
        help="override a setting in configuration file",
    )
    parser.add_argument(
        "--dump-metadata",
        action="store_true",
        help="dump generated metadata and exit",
    )
    args, argv = parser.parse_known_args(argv)
    if args.noconfig:
        return 1

    logger = logging.getLogger(__name__)

    sourcedir_absolute = os.path.abspath(args.sourcedir)
    confdir_absolute = os.path.abspath(args.confdir) if args.confdir is not None else sourcedir_absolute

    # Conf-overrides
    confoverrides = {}
    for d in args.define:
        key, _, value = d.partition("=")
        confoverrides[key] = value

    # Parse config
    config = load_sphinx_config(confdir_absolute, confoverrides, add_defaults=True)

    # Get relative paths to root of git repository
    gitroot = pathlib.Path(git.get_toplevel_path(cwd=sourcedir_absolute)).resolve()
    cwd_absolute = os.path.abspath(".")
    cwd_relative = os.path.relpath(cwd_absolute, str(gitroot))

    logger.debug("Git toplevel path: %s", str(gitroot))
    sourcedir = os.path.relpath(sourcedir_absolute, str(gitroot))
    logger.debug("Source dir (relative to git toplevel path): %s", str(sourcedir))
    if args.confdir:
        confdir = os.path.relpath(confdir_absolute, str(gitroot))
    else:
        confdir = sourcedir
    logger.debug("Conf dir (relative to git toplevel path): %s", str(confdir))
    conffile = os.path.join(confdir, "conf.py")

    # Get git references
    gitrefs = git.get_refs(
        str(gitroot),
        config.smv_tag_whitelist,
        config.smv_branch_whitelist,
        config.smv_remote_whitelist,
        files=(sourcedir, conffile),
    )

    # Order git refs
    if config.smv_prefer_remote_refs:
        gitrefs = sorted(gitrefs, key=lambda x: (not x.is_remote, *x))
    else:
        gitrefs = sorted(gitrefs, key=lambda x: (x.is_remote, *x))

    logger = logging.getLogger(__name__)

    with tempfile.TemporaryDirectory() as tmp:
        # Generate Metadata
        metadata = {}
        outputdirs = set()
        for gitref in gitrefs:
            # Clone Git repo
            repopath = os.path.join(tmp, gitref.commit)
            try:
                git.copy_tree(str(gitroot), gitroot.as_uri(), repopath, gitref)
            except (OSError, subprocess.CalledProcessError):
                logger.error(
                    "Failed to copy git tree for %s to %s",
                    gitref.refname,
                    repopath,
                )
                continue

            # Find config
            confpath = os.path.join(repopath, confdir)
            try:
                current_config = load_sphinx_config(confpath, confoverrides)
            except (OSError, sphinx_config.ConfigError):
                logger.error(
                    "Failed load config for %s from %s",
                    gitref.refname,
                    confpath,
                )
                continue

            # Ensure that there are not duplicate output dirs
            outputdir = config.smv_outputdir_format.format(
                ref=gitref,
                config=current_config,
            )
            if outputdir in outputdirs:
                logger.warning(
                    "outputdir '%s' for %s conflicts with other versions",
                    outputdir,
                    gitref.refname,
                )
                continue
            outputdirs.add(outputdir)

            # Get List of files
            source_suffixes = current_config.source_suffix
            if isinstance(source_suffixes, str):
                source_suffixes = [current_config.source_suffix]

            current_sourcedir = os.path.join(repopath, sourcedir)
            project = sphinx_project.Project(current_sourcedir, source_suffixes)
            metadata[gitref.name] = {
                "name": gitref.name,
                "version": current_config.version,
                "release": current_config.release,
                "rst_prolog": current_config.rst_prolog,
                "is_released": bool(re.match(config.smv_released_pattern, gitref.refname)),
                "source": gitref.source,
                "creatordate": gitref.creatordate.strftime(sphinx.DATE_FMT),
                "basedir": repopath,
                "sourcedir": current_sourcedir,
                "outputdir": os.path.join(os.path.abspath(args.outputdir), outputdir),
                "confdir": confpath,
                "docnames": list(project.discover()),
            }

        if args.dump_metadata:
            print(json.dumps(metadata, indent=2))  # noqa
            return 0

        if not metadata:
            logger.error("No matching refs found!")
            return 2

        # Write Metadata
        metadata_path = os.path.abspath(os.path.join(tmp, "versions.json"))
        with open(metadata_path, mode="w") as fp:
            json.dump(metadata, fp, indent=2)

        # Run Sphinx
        argv.extend(["-D", "smv_metadata_path={}".format(metadata_path)])
        for version_name, data in metadata.items():
            os.makedirs(data["outputdir"], exist_ok=True)

            defines = itertools.chain(*(("-D", string.Template(d).safe_substitute(data)) for d in args.define))

            current_argv = argv.copy()
            current_argv.extend(
                [
                    *defines,
                    "-D",
                    "smv_current_version={}".format(version_name),
                    "-c",
                    confdir_absolute,
                    data["sourcedir"],
                    data["outputdir"],
                    *args.filenames,
                ]
            )

            current_cwd = os.path.join(data["basedir"], cwd_relative)
            env = os.environ.copy()
            env.update(
                {
                    "SPHINX_MULTIVERSION_NAME": data["name"],
                    "SPHINX_MULTIVERSION_VERSION": data["version"],
                    "SPHINX_MULTIVERSION_RELEASE": data["release"],
                    "SPHINX_MULTIVERSION_SOURCEDIR": data["sourcedir"],
                    "SPHINX_MULTIVERSION_OUTPUTDIR": data["outputdir"],
                    "SPHINX_MULTIVERSION_CONFDIR": data["confdir"],
                }
            )

            if config.smv_prebuild_command:
                logger.debug("Running prebuild command: %r", config.smv_prebuild_command)
                subprocess.check_call(config.smv_prebuild_command, cwd=current_cwd, shell=True, env=env)

            logger.debug("Running sphinx-build with args: %r", current_argv)
            cmd = (
                sys.executable,
                *get_python_flags(),
                "-m",
                "sphinx",
                *current_argv,
            )
            subprocess.check_call(cmd, cwd=current_cwd, env=env)

            if config.smv_postbuild_command:
                logger.debug(
                    "Running postbuild command: %r",
                    config.smv_postbuild_command,
                )
                subprocess.check_call(config.smv_postbuild_command, cwd=current_cwd, shell=True, env=env)

    return 0
