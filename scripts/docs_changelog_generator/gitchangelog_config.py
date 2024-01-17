from gitchangelog.gitchangelog import Caret, FileFirstRegexMatch, FileRegexSubst, mustache

from docs_changelog_generator.config import config_context_var
from docs_changelog_generator.generate_changelog import (
    inject_author_usernames,
    inject_compare_link,
    inject_versions,
    subject_process,
)

config = config_context_var.get()

INSERT_POINT_REGEX = r"""(?isxu)
^
(
  \s*Changelog\s*(\n|\r\n|\r)        ## ``Changelog`` line
  ==+\s*(\n|\r\n|\r){2}              ## ``=========`` rest underline
)

(                     ## Match all between changelog and release rev
    (
      (?!
         (?<=(\n|\r))                ## look back for newline
         %(rev)s                     ## revision
         \s+
         \([0-9]+-[0-9]{2}-[0-9]{2}\)(\n|\r\n|\r)   ## date
           --+(\n|\r\n|\r)                          ## ``---`` underline
      )
      .
    )*
)

(?P<rev>%(rev)s)
""" % {"rev": r"v[0-9]+\.[0-9]+(\.[0-9]+)?"}

section_regexps = [
    ("🌟 New", [r"^[nN]ew\s*:\s*((dev|use?r|pkg|test|doc)\s*:\s*)?([^\n]*)$"]),
    ("🗒️ Changes", [r"^[cC]hg\s*:\s*((dev|use?r|pkg|test|doc)\s*:\s*)?([^\n]*)$"]),
    ("🐛 Bug Fixes", [r"^[fF]ix\s*:\s*((dev|use?r|pkg|test|doc)\s*:\s*)?([^\n]*)$"]),
    ("🚀 Features / Enhancements", [r"^[fF]eat\s*:\s*((dev|use?r|pkg|test|doc)\s*:\s*)?([^\n]*)$"]),
    ("📖 Docs", [r"^[dD]ocs?\s*:\s*((dev|use?r|pkg|test|doc)\s*:\s*)?([^\n]*)$"]),
    ("⚙️ Other", None),  ## Match all lines
]


subject_process = subject_process
unreleased_version_label = config.unreleased_version_label

revs = [Caret(FileFirstRegexMatch(config.output_file_path, INSERT_POINT_REGEX)), "HEAD"]

output_engine = mustache(str(config.mustache_template_path))
output_engine = inject_author_usernames(output_engine)
output_engine = inject_compare_link(output_engine)
output_engine = inject_versions(output_engine)

publish = FileRegexSubst(config.output_file_path, INSERT_POINT_REGEX, r"\1\o\g<rev>")
