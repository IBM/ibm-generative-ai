from pathlib import Path

import dotenv
from gitchangelog.gitchangelog import Caret, FileFirstRegexMatch, FileRegexSubst, mustache

from docs_changelog_generator.generate_changelog import (
    DIRNAME,
    inject_author_usernames,
    inject_compare_link,
    inject_versions,
    subject_process,
)

dotenv.load_dotenv()

MUSTACHE_TEMPLATE_PATH = str(DIRNAME / Path("mustache_rst.tpl"))
OUTPUT_FILE = Path(DIRNAME) / Path("../../documentation/source/changelog.rst")
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
    ("New", [r"^[nN]ew\s*:\s*((dev|use?r|pkg|test|doc)\s*:\s*)?([^\n]*)$"]),
    ("Changes", [r"^[cC]hg\s*:\s*((dev|use?r|pkg|test|doc)\s*:\s*)?([^\n]*)$"]),
    ("🐛 Bug Fixes", [r"^[fF]ix\s*:\s*((dev|use?r|pkg|test|doc)\s*:\s*)?([^\n]*)$"]),
    ("🚀 Features / Enhancements", [r"^[fF]eat\s*:\s*((dev|use?r|pkg|test|doc)\s*:\s*)?([^\n]*)$"]),
    ("📖 Docs", [r"^[dD]ocs?\s*:\s*((dev|use?r|pkg|test|doc)\s*:\s*)?([^\n]*)$"]),
    ("⚙️ Other", None),  ## Match all lines
]


subject_process = subject_process
unreleased_version_label = "(unreleased)"

revs = [Caret(FileFirstRegexMatch(OUTPUT_FILE, INSERT_POINT_REGEX)), "HEAD"]

output_engine = mustache(MUSTACHE_TEMPLATE_PATH)
output_engine = inject_author_usernames(output_engine)
output_engine = inject_compare_link(output_engine)
output_engine = inject_versions(output_engine)

publish = FileRegexSubst(OUTPUT_FILE, INSERT_POINT_REGEX, r"\1\o\g<rev>")
