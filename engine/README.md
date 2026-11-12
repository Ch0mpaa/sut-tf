# engine/

Reserved for the imported + patched TensorFold source tree.

Empty on purpose. Importing the source happens as its own commit so the
diff that follows (our KV-cache modification) is readable.

Procedure (planned):

```sh
git subtree add --prefix=engine \
  https://github.com/machinegenieorg/TensorFold.git <PR-836-merge-commit> --squash
```

...or equivalent. The chosen mechanism gets documented in `docs/LINEAGE.md`
alongside the exact commit hash.
