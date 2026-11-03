# Theory checks

Numerical checks behind the theory sections of the paper (exact family, restricted gain, bubbling, the 108-run tanh
set, exactness defect, free transverse modes). `REPRODUCE.md` says which paper number comes from which script.

They were written alongside the theory notes and copied here from branch `theory-notes` (34af5e0). Docstrings that
cite `docs/theory_notes.md` refer to the notes on that branch, which are not on `main`.

Run from this directory with the package on the path, for example:

    cd experiments/theory && PYTHONPATH=../../src python check_lorenz.py
