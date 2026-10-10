---
title: "Scripting with Python"
nav_order: 7
---

# Scripting with Python


Beyond the GUI and the `burrTxt` command-line solvers, BURRTOOLS can be
driven from Python. Building from source produces a `burrtools` extension
module that builds shapes and problems, solves them, and streams solutions
with on-the-fly disassembly:

`PYTHONPATH=build python3`

```
import burrtools
puzzle = burrtools.load("examples/PelikanBurr.xmpuzzle")
for sol in puzzle.problems[0].solve(disassemble=True):
    print(sol.solution_number, sol.level, sol.moves_text)
```

Puzzles can also be created entirely in memory and saved as `.xmpuzzle`
files. See "Python Wrapper" in `BUILD.md` in the source tree and the
runnable examples in `example_scripts/` for the full interface.
