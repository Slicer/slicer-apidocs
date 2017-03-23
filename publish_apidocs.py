#!/usr/bin/env python

import argparse
import errno
import os
import re
import shlex
import shutil
import subprocess
import tempfile
import textwrap

from contextlib import contextmanager


def mkdir_p(path):
    """Ensure directory ``path`` exists. If needed, parent directories
    are created.

    Adapted from http://stackoverflow.com/a/600612/1539918
    """
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:  # pragma: no cover
            raise


@contextmanager
def working_dir(directory=None, make_directory=False):
    """
    Context manager to save and optionally change the current directory.

    :param directory:
      Path to set as current working directory. If ``None``
      is passed, ``os.getcwd()`` is used instead.

    :param make_directory:
      If True, ``directory`` is created.
    """
    old_cwd = os.getcwd()

    if directory:
        if make_directory:
            mkdir_p(directory)
        os.chdir(directory)
        print("\ncwd: %s" % os.getcwd())
    yield
    os.chdir(old_cwd)


def execute(cmd, capture=False):
    print("\n%s" % cmd)
    check_func = subprocess.check_call
    extra_kwargs = {}
    if capture:
        check_func = subprocess.check_output
        extra_kwargs = {"stderr": subprocess.STDOUT}
    return check_func(cmd if isinstance(cmd, list) else shlex.split(cmd), **extra_kwargs)


def extract_slicer_version(slicer_src_dir):
    """Given a Slicer source director, extract <major>.<minor> version
    from top-level CMakeLists.txt
    """
    slicer_src_dir = os.path.abspath(slicer_src_dir)
    expressions = {part: re.compile(r"set\(Slicer_VERSION_%s \"([0-9]+)\"\)" % part.upper())
                   for part in ["major", "minor"]}
    parts = {}
    with open(slicer_src_dir + "/CMakeLists.txt") as fp:
        for line in fp.readlines(50):
            for part, expression in expressions.items():
                m = expression.match(line.strip())
                if m is not None:
                    parts[part] = m.group(1)
    return "{major}.{minor}".format(**parts)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=str, default="Slicer/Slicer")
    parser.add_argument("--branch", type=str, default="master")
    parser.add_argument("--tag", type=str)
    parser.add_argument("--slicer-src-dir", type=str)
    parser.add_argument("--publish-github-repo", type=str, default="slicer/apidocs.slicer.org")
    parser.add_argument("--publish-github-branch", type=str, default="gh-pages")
    parser.add_argument("--publish-github-token", type=str)
    parser.add_argument("--skip-build", action="store_true")
    args = parser.parse_args()

    clone_url = "git://github.com/%s" % args.repo
    repo = args.repo
    branch = args.branch
    tag = args.tag
    if tag:
        branch = tag

    publish_github_repo = args.publish_github_repo
    publish_github_url = "git://github.com/" + publish_github_repo
    publish_github_branch = args.publish_github_branch
    publish_github_token = args.publish_github_token
    if not publish_github_token:
        publish_github_token = os.environ.get("GITHUB_TOKEN", None)

    print("\nApidocs repository")
    print("   url: %s" % publish_github_url)
    print("  repo: %s" % publish_github_repo)
    print("  branch: %s" % publish_github_branch)

    slicer_src_dir = args.slicer_src_dir
    directory = "%s-%s" % (repo.replace("/", "-"), branch)
    root_dir = tempfile.gettempdir()
    apidocs_src_dir = os.path.dirname(os.path.abspath(__file__))
    apidocs_build_dir = root_dir + "/" + "%s-build" % directory
    if not slicer_src_dir:
        slicer_src_dir = root_dir + "/" + directory

    print("\nDirectories")
    print(" apidocs source dir: %s" % apidocs_src_dir)
    print(" apidocs  build dir: %s" % apidocs_build_dir)
    print(" Slicer  source dir: %s" % slicer_src_dir)

    skip_build = args.skip_build
    skip_publish = publish_github_token is None
    skip_publish_reason = ""
    if skip_publish:
        skip_publish_reason = ": Consider passing --publish-github-token argument " \
                              "or setting GITHUB_TOKEN env. variable"

    print("\nSkipping")
    print("    build: %s" % skip_build)
    print("  publish: %s%s" % (skip_publish, skip_publish_reason))

    # Get Slicer source
    if not os.path.exists(slicer_src_dir):
        execute("git clone %s --branch %s --depth 1 %s" % (clone_url, branch, slicer_src_dir))
    else:
        print("\nFound %s: skipping clone" % slicer_src_dir)

    with working_dir(slicer_src_dir):

        # Checkout expected version
        execute("git reset --hard %s" % tag if tag else "origin/" + branch)

        # Get commit
        slicer_src_commit = execute("git rev-parse --short HEAD", capture=True)
        print("Slicer commit: %s" % slicer_src_commit)

    if tag:
        version = ".".join(tag.lstrip("v").split(".")[:2])
    else:
        version = extract_slicer_version(slicer_src_dir)

    print("\nSlicer version: %s" % version)

    with working_dir(apidocs_build_dir, make_directory=True):

        # Configure the project
        execute([
            "cmake",
            "-DSlicer_SOURCE_DIR:PATH=%s" % os.path.join(root_dir, slicer_src_dir),
            "-DSlicer_VERSION:STRING=%s" % version,
            #  "-G", "Ninja",
            apidocs_src_dir
        ])

        # .. and build the doxygen documentation
        if not skip_build:
            execute("cmake --build . --target doc")

    with working_dir(apidocs_build_dir + "/Utilities/Doxygen"):

        # Checkout publishing repo
        if not os.path.exists("apidocs"):
            try:
                execute("git clone --branch %s --depth 1 %s apidocs" % (
                    publish_github_branch, publish_github_url), capture=True)
            except subprocess.CalledProcessError as exc_info:
                msg = "Remote branch %s not found in upstream origin" % publish_github_branch
                if msg not in exc_info.output:
                    raise
                # Create orphan branch
                execute("git clone %s apidocs" % publish_github_url)
                with working_dir("apidocs"):
                    execute("git symbolic-ref HEAD refs/heads/%s" % publish_github_branch)
                    os.remove(".git/index")
                    execute("git clean -fdx")

        with working_dir("apidocs"):

            # Update
            execute("git fetch origin")
            try:
                execute("git reset --hard origin/%s" % publish_github_branch, capture=True)
            except subprocess.CalledProcessError:
                pass

            # Rename html directory (html -> (vX.Y|<branch_name>)
            if os.path.exists("../html"):
                if os.path.exists(branch):
                    shutil.rmtree(branch)
                shutil.move("../html", branch)

            # Check if there are changes
            if not execute("git status --porcelain", capture=True) == "":

                execute("git add --all")

                sha = tag if tag else slicer_src_commit

                script_name = os.path.basename(__file__)

                msg = textwrap.dedent("""
                Slicer apidocs update for %s@%s

                It was automatically generated by the script ``%s`` [1]

                [1] https://github.com/Slicer/slicer-apidocs-builder/blob/master/%s
                """ % (repo, sha, script_name, script_name))
                execute("git commit -m '%s'" % msg)

            else:
                print("\nNo new changes to publish")

            # Publish
            xxx_token = len(publish_github_token) * "X"
            publish_github_url = "https://%s@github.com/%s" % (
                xxx_token, publish_github_repo)
            cmd = "git push %s %s" % (publish_github_url, publish_github_branch)
            try:
                print("\n%s" % cmd)
                subprocess.check_output(shlex.split(cmd.replace(xxx_token, publish_github_token)))
            except subprocess.CalledProcessError as exc_info:
                print("Failed to publish documentation. Return code is %s" % exc_info.returncode)


if __name__ == '__main__':
    main()