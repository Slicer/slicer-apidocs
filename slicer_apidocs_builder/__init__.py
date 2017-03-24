# -*- coding: utf-8 -*-

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
    print("\n> %s\n" % cmd)
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


def cli():
    parser = argparse.ArgumentParser()
    # Apidocs building parameters
    build_group = parser.add_argument_group('Apidocs Building')
    build_group.add_argument(
        "--slicer-repo-name", type=str, default="Slicer/Slicer",
        help="Slicer repository to document (default: Slicer/Slicer)."
    )
    build_group.add_argument(
        "--slicer-repo-dir", type=str,
        help="Slicer sources checkout to reuse. By default, checkout source in TEMP directory."
    )
    build_group.add_argument(
        "--slicer-repo-branch", type=str, default="master",
        help="Slicer branch to document (default: master)"
    )
    build_group.add_argument(
        "--slicer-repo-tag", type=str,
        help="Slicer tag to document. If specified --branch is ignored."
    )
    build_group.add_argument(
        "--skip-build", action="store_true",
        help="If specified, skip generation of HTML and reuse existing files."
    )
    # apidocs publishing parameters
    publish_group = parser.add_argument_group('Apidocs Publishing')
    publish_group.add_argument(
        "--publish-github-username", type=str, default="Slicer Bot",
        help="Github name to associate with the commits (default: Slicer Bot)"
    )
    publish_group.add_argument(
        "--publish-github-useremail", type=str, default="slicerbot@slicer.org",
        help="Github email to associate with the commits (default: slicerbot@slicer.org)"
    )
    publish_group.add_argument(
        "--publish-github-repo", type=str, default="slicer/apidocs.slicer.org",
        help="Github repository hosting generated HTML documentation "
             "(default: slicer/apidocs.slicer.org)"
    )
    publish_group.add_argument(
        "--publish-github-branch", type=str, default="gh-pages",
        help="Github branch hosting generated HTML documentation (default: gh-pages)"
    )
    publish_group.add_argument(
        "--publish-github-token", type=str,
        default=os.environ.get("PUBLISH_GITHUB_TOKEN", None),
        help="GitHub Token allowing to publish generated documentation "
             "(default: PUBLISH_GITHUB_TOKEN env. variable)"
    )
    args = parser.parse_args()

    # apidocs building parameters
    slicer_repo_clone_url = "git://github.com/%s" % args.slicer_repo_name
    slicer_repo_name = args.slicer_repo_name
    slicer_repo_branch = args.slicer_repo_branch
    slicer_repo_tag = args.slicer_repo_tag
    if slicer_repo_tag:
        slicer_repo_branch = slicer_repo_tag

    # Directories
    slicer_repo_dir = args.slicer_repo_dir
    directory = "%s-%s" % (slicer_repo_name.replace("/", "-"), slicer_repo_branch)
    root_dir = tempfile.gettempdir()
    apidocs_src_dir = root_dir + "/" + "%s-src" % directory
    apidocs_build_dir = root_dir + "/" + "%s-build" % directory
    if not slicer_repo_dir:
        slicer_repo_dir = root_dir + "/" + directory

    print("\nApidocs building parameters")
    print("  * repo_clone_url ..............: %s" % slicer_repo_clone_url)
    print("  * repo_name....................: %s" % slicer_repo_name)
    print("  * repo_branch .................: %s" % slicer_repo_branch)
    print("  * repo_tag ....................: %s" % slicer_repo_tag)
    print("  * repo_dir ....................: %s" % slicer_repo_dir)
    print("  * apidocs_src_dir .............: %s" % apidocs_src_dir)
    print("  * apidocs_build_dir ...........: %s" % apidocs_build_dir)

    # apidocs publishing
    publish_github_username = args.publish_github_username
    publish_github_useremail = args.publish_github_useremail
    publish_github_repo = args.publish_github_repo
    publish_github_url = "git://github.com/" + publish_github_repo
    publish_github_branch = args.publish_github_branch
    publish_github_token = args.publish_github_token

    publish_github_token_msg = "(missing)"
    if publish_github_token:
        publish_github_token_msg = "x" * len(publish_github_token) + " (obfuscated)"

    print("\nApidocs publishing parameters")
    print("  * username ....................: %s" % publish_github_username)
    print("  * useremail ...................: %s" % publish_github_useremail)
    print("  * url .........................: %s" % publish_github_url)
    print("  * repo ........................: %s" % publish_github_repo)
    print("  * branch ......................: %s" % publish_github_branch)
    print("  * github_token.................: %s" % publish_github_token_msg)



    # Summary
    skip_build = args.skip_build
    skip_build_reason = ""

    skip_publish = publish_github_token is None
    skip_publish_reason = "[Missing GitHub token]" if skip_publish else ""

    skip_clone = os.path.exists(slicer_repo_dir)
    skip_clone_reason = "[Found existing checkout: %s]" % slicer_repo_dir if skip_clone else ""

    print("\nSummary:")
    print("  * building doxygen ............: %s   %s" % (not skip_build, skip_build_reason))
    print("  * publishing on github.io .....: %s   %s" % (not skip_publish, skip_publish_reason))
    print("  * cloning Slicer repository ...: %s   %s" % (not skip_clone, skip_clone_reason))

    apidocs_cmakelists = os.path.dirname(os.path.abspath(__file__)) + "/CMakeLists.txt"
    print("\nCopying %s into %s" % (apidocs_cmakelists, apidocs_src_dir))
    mkdir_p(apidocs_src_dir)
    shutil.copy(apidocs_cmakelists, apidocs_src_dir)


    # Get Slicer source
    if not skip_clone:
        execute("git clone %s --branch %s --depth 1 %s" % (slicer_repo_clone_url, slicer_repo_branch, slicer_repo_dir))

    with working_dir(slicer_repo_dir):

        # Checkout expected version
        execute("git reset --hard %s" % (slicer_repo_tag if slicer_repo_tag else "origin/" + slicer_repo_branch))

        # Get commit
        slicer_repo_head_sha = execute("git rev-parse HEAD", capture=True)
        print("slicer_repo_head_sha: %s" % slicer_repo_head_sha)

    if slicer_repo_tag:
        version = ".".join(slicer_repo_tag.lstrip("v").split(".")[:2])
    else:
        version = extract_slicer_version(slicer_repo_dir)

    print("\nSlicer version: %s" % version)

    with working_dir(apidocs_build_dir, make_directory=True):

        def configure():
            execute([
                "cmake",
                "-DSlicer_SOURCE_DIR:PATH=%s" % os.path.join(root_dir, slicer_repo_dir),
                "-DSlicer_VERSION:STRING=%s" % version,
                #  "-G", "Ninja",
                apidocs_src_dir
            ])

        def build():
            execute("cmake --build . --target doc")

        configure()

        if not skip_build:
            build()

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

            # Setup user.name and user.email
            execute("git config user.email '%s'" % publish_github_useremail)
            execute("git config user.name '%s'" % publish_github_username)

            # Update
            execute("git fetch origin")
            try:
                execute("git reset --hard origin/%s" % publish_github_branch, capture=True)
            except subprocess.CalledProcessError:
                pass

            # Rename html directory (html -> (vX.Y|<branch_name>)
            if os.path.exists("../html"):
                if os.path.exists(slicer_repo_branch):
                    shutil.rmtree(slicer_repo_branch)
                shutil.move("../html", slicer_repo_branch)

            # Check if there are changes
            if not execute("git status --porcelain", capture=True) == "":

                execute("git add --all")

                sha = slicer_repo_tag if slicer_repo_tag else slicer_repo_head_sha[:8]

                msg = textwrap.dedent("""
                Slicer apidocs update for %s@%s

                It was automatically generated by the script ``slicer-apidocs-builder`` [1]

                [1] https://github.com/Slicer/slicer-apidocs-builder
                """ % (slicer_repo_name, sha))
                execute("git commit -m '%s'" % msg)

            else:
                print("\nNo new changes to publish")

            # Publish
            if skip_publish:
                return
            xxx_token = len(publish_github_token) * "X"
            publish_github_url = "https://%s@github.com/%s" % (
                xxx_token, publish_github_repo)
            cmd = "git push %s %s" % (publish_github_url, publish_github_branch)
            try:
                print("\n%s" % cmd)
                subprocess.check_output(shlex.split(cmd.replace(xxx_token, publish_github_token)))
            except subprocess.CalledProcessError as exc_info:
                print("Failed to publish documentation. Return code is %s" % exc_info.returncode)


def main():
    try:
        cli()
    except subprocess.CalledProcessError as exc_info:
        print("\nExit code: %s" % exc_info.returncode)
        if exc_info.output:
            print("\nOutput: %s" % exc_info.output)
        raise SystemExit(exc_info.returncode)
    except KeyboardInterrupt:
        print("interrupt received, stopping...")


if __name__ == '__main__':
    main()
