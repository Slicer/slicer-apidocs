# -*- coding: utf-8 -*-

from __future__ import absolute_import

import argparse
import os
import re
import shlex
import shutil
import subprocess
import tempfile
import textwrap

import github3

from .utils import execute, mkdir_p, working_dir


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


def _apidocs_build_doxygen(
        apidocs_src_dir=None,
        apidocs_build_dir=None,
        slicer_repo_clone_url=None,
        slicer_repo_dir=None,
        slicer_repo_branch=None,
        slicer_repo_tag=None,
        skip_clone=False,
        skip_build=False
):
    assert apidocs_src_dir
    assert apidocs_build_dir
    assert slicer_repo_clone_url
    assert slicer_repo_dir
    assert slicer_repo_branch
    # slicer_repo_tag can be unspecified

    apidocs_cmakelists = os.path.dirname(os.path.abspath(__file__)) + "/CMakeLists.txt"
    print("\nCopying %s into %s" % (apidocs_cmakelists, apidocs_src_dir))
    mkdir_p(apidocs_src_dir)
    shutil.copy(apidocs_cmakelists, apidocs_src_dir)

    # Get Slicer source
    if not skip_clone:
        execute("git clone %s --branch %s --depth 1 %s" % (
            slicer_repo_clone_url, slicer_repo_branch, slicer_repo_dir))

    with working_dir(slicer_repo_dir):

        # Checkout expected version
        execute("git reset --hard %s" % (
            slicer_repo_tag if slicer_repo_tag else "origin/" + slicer_repo_branch))

    if slicer_repo_tag:
        version = ".".join(slicer_repo_tag.lstrip("v").split(".")[:2])
    else:
        version = extract_slicer_version(slicer_repo_dir)

    print("\nSlicer version: %s" % version)

    with working_dir(apidocs_build_dir, make_directory=True):

        def configure():
            execute([
                "cmake",
                "-DSlicer_SOURCE_DIR:PATH=%s" % slicer_repo_dir,
                "-DSlicer_VERSION:STRING=%s" % version,
                #  "-G", "Ninja",
                apidocs_src_dir
            ])

        def build():
            execute("cmake --build . --target doc")

        configure()

        if not skip_build:
            build()

    return apidocs_build_dir + "/Utilities/Doxygen"


def _apidocs_publish_doxygen(
        doxygen_output_dir=None,
        publish_github_repo_url=None,
        publish_github_repo_name=None,
        publish_github_repo_branch=None,
        publish_github_username=None, publish_github_useremail=None,
        publish_github_token=None,
        publish_github_subdir=None,
        slicer_repo_sha_ref=None,
        skip_publish=False,
):
    assert os.path.isdir(doxygen_output_dir)
    assert publish_github_repo_url
    assert publish_github_repo_name
    assert publish_github_repo_branch
    assert publish_github_username
    assert publish_github_useremail
    assert publish_github_token
    assert publish_github_subdir
    assert slicer_repo_sha_ref

    with working_dir(doxygen_output_dir):

        # Checkout publishing repo
        if not os.path.exists("apidocs"):
            try:
                execute("git clone --branch %s --depth 1 %s apidocs" % (
                    publish_github_repo_branch, publish_github_repo_url), capture=True)
            except subprocess.CalledProcessError as exc_info:
                msg = "Remote branch %s not found in upstream origin" % publish_github_repo_branch
                if msg not in exc_info.output:
                    raise
                # Create orphan branch
                execute("git clone %s apidocs" % publish_github_repo_url)
                with working_dir("apidocs"):
                    execute("git symbolic-ref HEAD refs/heads/%s" % publish_github_repo_branch)
                    os.remove(".git/index")
                    execute("git clean -fdx")

        with working_dir("apidocs"):

            # Setup user.name and user.email
            execute("git config user.email '%s'" % publish_github_useremail)
            execute("git config user.name '%s'" % publish_github_username)

            # Update
            execute("git fetch origin")
            try:
                execute("git reset --hard origin/%s" % publish_github_repo_branch, capture=True)
            except subprocess.CalledProcessError:
                pass

            # Rename html directory (html -> (vX.Y|<branch_name>)
            if os.path.exists("../html"):
                if os.path.exists(publish_github_subdir):
                    shutil.rmtree(publish_github_subdir)
                shutil.move("../html", publish_github_subdir)

            # Check if there are changes
            if not execute("git status --porcelain", capture=True) == "":

                execute("git add --all")

                msg = textwrap.dedent("""
                Slicer apidocs update for %s

                It was automatically generated by the script ``slicer-apidocs-builder`` [1]

                [1] https://github.com/Slicer/slicer-apidocs-builder
                """ % slicer_repo_sha_ref)
                execute("git commit -m '%s'" % msg)

            else:
                print("\nNo new changes to publish")

            # Publish
            if skip_publish:
                return
            xxx_token = len(publish_github_token) * "X"
            publish_github_push_url = "https://%s@github.com/%s" % (
                xxx_token, publish_github_repo_name)
            xxx_cmd = "git push %s %s" % (publish_github_push_url, publish_github_repo_branch)
            try:
                print("\n%s" % xxx_cmd)
                subprocess.check_output(
                    shlex.split(xxx_cmd.replace(xxx_token, publish_github_token)),
                    stderr=subprocess.STDOUT
                )
            except subprocess.CalledProcessError as exc_info:
                raise subprocess.CalledProcessError(
                    exc_info.returncode, xxx_cmd, "Failed to publish documentation.")


def _apidocs_status_update(
        status_update_state,
        status_update_repo_name=None,
        status_update_revision=None,
        status_update_revision_remark="",
        status_update_target_url_base=None,
        status_update_target_url_path=None,
        status_update_token=None
):
    assert status_update_state
    missing = (not status_update_repo_name
               or not status_update_revision
               or not status_update_target_url_base
               or not status_update_target_url_path
               or not status_update_token)

    if not status_update_repo_name:
        status_update_repo_name = "(missing)"

    if not status_update_revision:
        status_update_revision = "(missing)"

    if not status_update_target_url_base:
        status_update_target_url_base = "(missing)"

    if not status_update_target_url_path:
        status_update_target_url_path = "(missing)"

    if status_update_token:
        status_update_token_obfuscated = "x" * len(status_update_token)
    else:
        status_update_token_obfuscated = "(missing)"

    status_update_target_url = status_update_target_url_base + "/" + status_update_target_url_path

    print("\nApidocs status update parameters")
    print("  * state .......................: %s" % status_update_state)
    print("  * repo_name ...................: %s" % status_update_repo_name)
    print("  * revision ....................: %s  %s" % (status_update_revision,
                                                         status_update_revision_remark))
    print("  * target_url_base .............: %s" % status_update_target_url_base)
    print("  * target_url_path .............: %s" % status_update_target_url_path)
    print("  * target_url ..................: %s" % status_update_target_url)
    print("  * github_token ................: %s" % status_update_token_obfuscated)

    if missing:
        print("\nAborting: parameters are missing")
        return

    owner, repository = status_update_repo_name.split("/")
    gh = github3.GitHub()
    gh.login(token=status_update_token)
    repository = gh.repository(owner, repository)

    messages = {
        "pending": "API documentation is being generated",
        "failure": "API documentation failed to be generated",
        "success": "API documentation published"
    }

    response = repository.create_status(
        status_update_revision,
        state=status_update_state,
        context="slicer/apidocs",
        description=messages[status_update_state],
        target_url=status_update_target_url
    )
    if response is None:
        raise RuntimeError("Failed to create GitHub status")


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
        "--slicer-repo-branch", type=str,
        help="Slicer branch to document (example: master)"
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
        "--publish-github-repo-name", type=str, default="slicer/apidocs.slicer.org",
        help="Github repository hosting generated HTML documentation "
             "(default: slicer/apidocs.slicer.org)"
    )
    publish_group.add_argument(
        "--publish-github-repo-branch", type=str, default="gh-pages",
        help="Github branch hosting generated HTML documentation (default: gh-pages)"
    )
    publish_group.add_argument(
        "--publish-github-token", type=str,
        default=os.environ.get("PUBLISH_GITHUB_TOKEN", None),
        help="GitHub Token allowing to publish generated documentation "
             "(default: PUBLISH_GITHUB_TOKEN env. variable)"
    )
    # apidocs builder overall status update
    status_update_group = parser.add_argument_group('Apidocs Status Update')
    status_update_group.add_argument(
        "--status-update-state", type=str, choices=["pending", "failure", "success"],
        help="State of the apidocs"
    )
    status_update_group.add_argument(
        "--status-update-target-url-base", type=str, default="http://apidocs.slicer.org",
        help="URL to associate with the state update. (default: http://apidocs.slicer.org)"
    )
    status_update_group.add_argument(
        "--status-update-target-url-path", type=str,
        help="Path appended to target base URL."
             "(default: based on value of --slicer-repo-branch and --slicer-repo-tag)"
    )
    status_update_group.add_argument(
        "--status-update-revision", type=str,
        help="Slicer revision to update"
             "(default to HEAD of Slicer source checkout. See --slicer-repo-dir)"
    )
    status_update_group.add_argument(
        "--status-update-repo-name", type=str,
        help="Slicer repo name to update (default to --slicer-repo-name)"
    )
    status_update_group.add_argument(
        "--status-update-token", type=str,
        default=os.environ.get("STATUS_UPDATE_GITHUB_TOKEN", None),
        help="GitHub token allowing to update status "
             "(default: STATUS_UPDATE_GITHUB_TOKEN env. variable)"
    )
    args = parser.parse_args()

    # Slicer repo name, branch and tag
    slicer_repo_name = args.slicer_repo_name
    slicer_repo_branch = args.slicer_repo_branch
    slicer_repo_tag = args.slicer_repo_tag
    if slicer_repo_tag:
        slicer_repo_branch = slicer_repo_tag

    # Root directory
    root_dir = tempfile.gettempdir()
    directory = "%s-%s" % (slicer_repo_name.replace("/", "-"), slicer_repo_branch)

    # Default value for Slicer source directory
    slicer_repo_dir = args.slicer_repo_dir
    if not slicer_repo_dir:
        slicer_repo_dir = root_dir + "/" + directory
    slicer_repo_dir = os.path.abspath(slicer_repo_dir)

    # apidocs status update
    if args.status_update_state:

        status_update_state = args.status_update_state
        status_update_repo_name = args.status_update_repo_name
        status_update_revision = args.status_update_revision
        status_update_token = args.status_update_token
        status_update_target_url_base = args.status_update_target_url_base
        status_update_target_url_path = args.status_update_target_url_path

        if not status_update_repo_name:
            status_update_repo_name = slicer_repo_name

        if not status_update_target_url_path:
            status_update_target_url_path = slicer_repo_branch

        status_update_revision_remark = ""
        if not status_update_revision:
            if os.path.exists(slicer_repo_dir + "/.git"):
                with working_dir(slicer_repo_dir):
                    status_update_revision = execute(
                        "git rev-parse HEAD", capture=True, verbose=False).strip()

                status_update_revision_remark = \
                    "(extracted from '<slicer_repo_dir:%s>')" % slicer_repo_dir
            else:
                status_update_revision_remark = \
                    "('<slicer_repo_dir:%s/.git>' does not exists)" % slicer_repo_dir

        _apidocs_status_update(
            status_update_state,
            status_update_token=status_update_token,
            status_update_repo_name=status_update_repo_name,
            status_update_revision=status_update_revision,
            status_update_revision_remark=status_update_revision_remark,
            status_update_target_url_base=status_update_target_url_base,
            status_update_target_url_path=status_update_target_url_path
        )
        return

    # apidocs building parameters
    slicer_repo_clone_url = "git://github.com/%s" % args.slicer_repo_name

    # Apidocs directories
    apidocs_src_dir = root_dir + "/" + "%s-src" % directory
    apidocs_build_dir = root_dir + "/" + "%s-build" % directory

    # apidocs publishing
    publish_github_username = args.publish_github_username
    publish_github_useremail = args.publish_github_useremail
    publish_github_repo_name = args.publish_github_repo_name
    publish_github_repo_branch = args.publish_github_repo_branch
    publish_github_repo_url = "git://github.com/" + publish_github_repo_name
    publish_github_token = args.publish_github_token

    # Skipping
    skip_build = args.skip_build
    skip_publish = publish_github_token is None
    skip_clone = os.path.exists(slicer_repo_dir)

    def _apidocs_display_report():

        if not skip_build:
            print("\nApidocs building parameters")
            print("  * repo_clone_url ..............: %s" % slicer_repo_clone_url)
            print("  * repo_name....................: %s" % slicer_repo_name)
            print("  * repo_branch .................: %s" % slicer_repo_branch)
            print("  * repo_tag ....................: %s" % slicer_repo_tag)
            print("  * repo_dir ....................: %s" % slicer_repo_dir)
            print("  * apidocs_src_dir .............: %s" % apidocs_src_dir)
            print("  * apidocs_build_dir ...........: %s" % apidocs_build_dir)

        if publish_github_token:
            publish_github_token_obfuscated = "x" * len(publish_github_token)
        else:
            publish_github_token_obfuscated = "(missing)"

        print("\nApidocs publishing parameters")
        print("  * username ....................: %s" % publish_github_username)
        print("  * useremail ...................: %s" % publish_github_useremail)
        print("  * repo_url ....................: %s" % publish_github_repo_url)
        print("  * repo_name ...................: %s" % publish_github_repo_name)
        print("  * repo_branch .................: %s" % publish_github_repo_branch)
        print("  * github_token.................: %s" % publish_github_token_obfuscated)

        # Summary
        skip_build_reason = "(--skip-build argument)" if skip_build else ""
        skip_publish_reason = "(missing GitHub token)" if skip_publish else ""
        skip_clone_reason = "(found existing checkout: %s)" % slicer_repo_dir if skip_clone else ""

        print("\nSummary:")
        print("  * cloning Slicer repository ...: %s   %s" % (not skip_clone, skip_clone_reason))
        print("  * building doxygen ............: %s   %s" % (not skip_build, skip_build_reason))
        print("  * publishing on github.io .....: %s   %s" % (not skip_publish, skip_publish_reason))

    _apidocs_display_report()

    doxygen_output_dir = _apidocs_build_doxygen(
        apidocs_src_dir=apidocs_src_dir, apidocs_build_dir=apidocs_build_dir,
        slicer_repo_clone_url=slicer_repo_clone_url,
        slicer_repo_dir=slicer_repo_dir,
        slicer_repo_branch=slicer_repo_branch, slicer_repo_tag=slicer_repo_tag,
        skip_clone=skip_clone, skip_build=skip_build
    )

    with working_dir(slicer_repo_dir):
        slicer_repo_head_sha = execute("git rev-parse HEAD", capture=True)
        print("slicer_repo_head_sha: %s" % slicer_repo_head_sha)

    slicer_repo_sha_ref = "%s@%s" % (
        slicer_repo_name, slicer_repo_tag if slicer_repo_tag else slicer_repo_head_sha[:8])

    _apidocs_publish_doxygen(
        doxygen_output_dir=doxygen_output_dir,
        publish_github_repo_url=publish_github_repo_url,
        publish_github_repo_name=publish_github_repo_name,
        publish_github_repo_branch=publish_github_repo_branch,
        publish_github_username=publish_github_username,
        publish_github_useremail=publish_github_useremail,
        publish_github_token=publish_github_token,
        publish_github_subdir=slicer_repo_branch,
        slicer_repo_sha_ref=slicer_repo_sha_ref,
        skip_publish=skip_publish,
    )

    # Since building the doxygen documentation outputs a lot of text,
    # for convenience let's display the report again.
    if not skip_build:
        _apidocs_display_report()


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
