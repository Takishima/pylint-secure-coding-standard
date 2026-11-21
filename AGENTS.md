# Instructions for AI coding agents

## Every pull request needs a changelog fragment

Do not edit `CHANGELOG.md`. Add a new file in `changelog.d/` instead. CI fails without one. Dependabot and release pull requests do not need one.

- **Name:** `changelog.d/+<short-description>.<type>.md`
- **Type:** `added`, `changed`, `deprecated`, `removed`, `fixed`, `security`, or `repository` (CI, tooling, tests, docs)
- **Content:** one sentence on one line, with no heading and no leading `- `

Example, `changelog.d/+shelve-open.fixed.md`:

```markdown
Fix false positive when `shelve.open()` is called with `flag='r'`
```

Use one file per change. Do not run `towncrier build`, and do not touch other fragments.

## Development

- Test: `python -m pip install -e .[test]`, then `python -m pytest`
- Lint: `pre-commit run --all-files`
- New checks need tests and a row in the codes table of `README.md`
- Do not tag, set versions or publish by hand: the release workflows do that
