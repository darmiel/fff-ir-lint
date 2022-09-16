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

> **Note**: Specify `github` for format

![img](./assets/format_github.png)

### Simple

> **Note**: Specify `simple` for format

```
→ python3 main.py simple remote.ir                                                           [18f2be4]
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
