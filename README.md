![Header-Dark](./assets/bg_dark.png#gh-dark-mode-only)
![Header-Light](./assets/bg_light.png#gh-light-mode-only)

# fff-ir-lint

Finds common mistakes in `.ir` files ([FlipperFormat](https://github.com/Eng1n33r/flipperzero-firmware/tree/dev/lib/flipper_format)).

## Usage

> **Note**: No dependencies needed. (`sys`, `re`, `io`, `typing`, `difflib`)

```shell
$ python3 main.py <format> [file 1] [file 2] ... [file n]
```

## Formats

### GitHub

> **Note**: Specify `github` or `github2` for format

![GitHub-Dark](./assets/gh_dark.png#gh-dark-mode-only)
![GitHub-Light](./assets/gh_light.png#gh-light-mode-only)

### Simple

> **Note**: Specify `simple` for format

```
→ python3 main.py simple remote.ir
*********************************
[lint] checking 'remote.ir' [1/1]
Error in line 19
'protocol:NEC'
         ↑
         [error]: space missing after ':'
[suggested] 'protocol: NEC'
---
Error in line 19
'protocol:NEC'
 ↑↑↑↑↑↑↑↑
 [error]: key 'type' expected
[suggested] 'type: ...'
---
[lint] found 2 warnings/errors in file.
*********************************
```

## CI/CD

An example GitHub Actions Workflow can be found [here](./examples/gh_actions_pr_lint_review.yaml).

The linter should work in a CI/CD pipeline.
Just put the example in your repo under the `.github/workflows` directory and 
[enable](https://docs.github.com/en/actions/managing-workflow-runs/disabling-and-enabling-a-workflow)
actions in the repo if necessary.

If a pull request is created in which `.ir` files are modified, the linter checks the modified (or newly created) `.ir` files.

If errors are found, they are appended as a comment to the PR and the PR is set to **Requested Changes**.