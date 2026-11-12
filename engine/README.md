# engine/

Reserved for the imported + patched TensorFold source tree.

Empty on purpose. During development the source is cloned beside the repo
(`~/sut-tf-work/sut-tf/engine-src/` on ailab, `.gitignore`d here) so we can
iterate without polluting history. Once we have a build that compiles and
serves, we import the source into this directory as its own commit — one
distinct commit for the import, one or more commits for our modifications,
so the diff is readable.

## Current dev layout on ailab

```
~/sut-tf-work/
  sut-tf/           this repo (cloned)
    engine-src/     upstream TensorFold clone (.gitignored, not imported yet)
    engine/         empty; the eventual home for the imported source
```

## Planned import mechanism

To be chosen after the first successful ailab build. Candidates:

- `git subtree add --prefix=engine <url> <ref> --squash`
- vendored source copy with a VERSION file
- git submodule (least preferred — downstream users have to recurse)

Decision + exact commit hash will be recorded in `docs/LINEAGE.md`.
