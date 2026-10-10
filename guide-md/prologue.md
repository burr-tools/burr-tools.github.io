---
title: "Prologue"
nav_order: 0
---

# Prologue


*to my mother (1950-2005)*

What are BURRTOOLS? BURRTOOLS consists of two main parts. On the one hand
there is a program that assembles and disassembles burr-type puzzles. That
program contains a graphical user interface (GUI) which allows creating and
editing puzzle definitions, solving the puzzle, and the display and animation
of the solutions found. This is probably the most interesting part for most
people. On the other hand there is also a C++ library that may help with the
search for and design of new puzzles. This library contains all the necessary
tools to write programs that do what the graphical interface does (and more).

This document describes the graphical program. It contains
descriptions of all concepts and explains how to use them in the GUI program.

For those that want to use or just look at the library part of BURRTOOLS there
are doxygen comments within the library source code. Besides the user interface
they explain the basic ideas of the library and also some of the algorithms
used. But this is only for the interested and not required for the understanding
of the GUI.

But first a little bit of history of this program. There are already two
programs with similar functionality to BURRTOOLS can do. One is BCPBOX/GENDA
written by Bill Cutler. Cutler's programs are very versatile, they even can
handle different space grids. The other one is PUZZLESOLVER3D by André van
Kammen. I had bought this program a while ago and have generally been quite
satisfied with it. I have taken over quite some ideas from the GUI that André
developed. So why another program, you might ask. Here are a few reasons:

- The available programs are not for LINUX, which is my operating system of
  choice, they only run on Windows so they leave out all users of OSX, Unix and
  all those other operating systems,
- the available programs are binary only programs and hence it is quite hard to
  do more complex research or design tasks,
- the programs do cost money,
- PUZZLESOLVER3D seems to be abandoned. There hasn't been any update for quite
  a while, its website is also gone by now,
- PUZZLESOLVER3D has some nasty limits to the shape, sizes, and the number of
  possible placements.


Anyway, I was not completely satisfied with the available software. Then in
summer 2003 a German computer magazine started a competition to write a program
that counts the number of solutions to a merchandising puzzle as fast as
possible. My program wasn't the fastest but it was the starting point for
BURRTOOLS.

As there are many people out there that are a lot more creative than I am and
that could use a program like this to design nice puzzles, I decided to make it
public and free (see www.gnu.org).

I added a GUI that can work on many operating systems, including LINUX and
WINDOWS. This has the disadvantage that the GUI looks a bit different from what
the normal WINDOWS user is used to, so stay calm if things look a bit unusual,
they behave in fact quite similar to how a normal WINDOWS-program behaves.

Lately 2 people played important roles in the development of the program.
These 2 are Ronald Kint-Bruynseels and Derek Bosch. Ronald has rewritten this
manual and has generally contributed lots of well organized suggestions. Derek
is responsible for the OSX port of the program. Without him there would be no
binary for this operating system available.

I want to thank both of them for their work. I also want to thank all the other
people that have sent in bug reports, suggestions and praise. Their input is
very welcome and crucial to the further development of the program.

Now BURRTOOLS has become a kind of de-facto standard in the puzzle World. Many
designer seem to use it. It is suitable for transmitting puzzle ideas from the
designer to the producer or a friend for comments.

BURRTOOLS now also has a few capabilities that no other puzzle program has. It
can do movement analysis of some non-cube-based grids (like the triangle-grid).
It can produce STL output which can directly go to the 3D printer which become
more and more sensible priced and which can quickly print out the most
complicated shapes for quick testing of puzzle ideas.

It has taken all those years since 2003 for BURRTOOLS to reach the current
state and there is no end in sight for new features that could be added. I hope
that you enjoy your puzzle experience with BURRTOOLS.

Andreas Röver
