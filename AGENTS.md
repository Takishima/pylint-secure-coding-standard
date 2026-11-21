# Instructions for AI coding agents

Pylint plugin made of a single module, `pylint_secure_coding_standard.py`, with its tests in `tests/`.

## Changelog fragment: required in every pull request

Every change needs a changelog fragment in `changelog.d/`. The "Changelog fragment" job fails pull requests that do not
add one, or that edit `CHANGELOG.md`.

1. **Never edit `CHANGELOG.md`.** It is generated from the fragments when a release is drafted.

2. Create one file per change, named `changelog.d/+<short-description>.<type>.md`. If you already know the pull request
   or issue number, use `changelog.d/<number>.<type>.md` instead.

3. `<type>` must be one of:

   | Type         | Use it for                                                        |
   | ------------ | ----------------------------------------------------------------- |
   | `added`      | New checks, options or other features                             |
   | `changed`    | Changes in existing behaviour (including dropped Python versions) |
   | `deprecated` | Features that will be removed in a future release                 |
   | `removed`    | Features that were removed                                        |
   | `fixed`      | Bug fixes                                                         |
   | `security`   | Fixes for vulnerabilities                                         |
   | `repository` | CI, tooling, tests, documentation: anything users will not notice |

4. The file contains one sentence of Markdown on a single line, written like the existing entries of `CHANGELOG.md`:
   no heading, no leading `- `, code in backticks. Example for `changelog.d/+shelve-open.fixed.md`:

   ```markdown
   Fix false positive when `shelve.open()` is called with `flag='r'`
   ```

Also:

- Add the fragment in the same commit or pull request as the change it describes, and update it if the change evolves.
- Several changes in one pull request means several fragment files.
- Do not delete or rewrite fragments that belong to other changes.
- Never run `towncrier build` without `--draft`: it rewrites `CHANGELOG.md` and deletes the fragments, which is the job
  of the "Draft new release" workflow. `python -m towncrier build --draft --version 0.0.0` shows a preview.
- Release pull requests (`release/*` branches) do not need a fragment.
- Do not add the `Skip-Changelog` label yourself to get around the check; that is the maintainer's decision.

## Development

- Install and test: `python -m pip install -e .[test]`, then `python -m pytest`.
- Lint and format: `pre-commit run --all-files`.
- New or changed checks must be covered by tests and listed in the codes table of `README.md`.
- The version comes from Git tags (`setuptools_scm`): do not hard-code it anywhere.
- Releases are made by the "Draft new release" and "Publish new release" workflows: do not create tags, edit release
  sections of the changelog or upload to PyPI by hand.
