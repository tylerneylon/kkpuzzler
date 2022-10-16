# kkpuzzler

*A terminal-based tool to edit KenKen puzzles.*

This is a little tool I made because I'd like to write a book or
two about KenKen puzzles, which I enjoy. Currently this tool
allows you to quickly type in a KenKen puzzle, to automatically
solve that puzzle, and to create a pdf of that puzzle.

In the future, I am interested in adding features that could assist
in these things:
* Explaining a human-friendly step-by-step solution to a puzzle
* Evaluating the difficulty of a puzzle
* Coming up with new puzzles of a given difficulty

## Usage

This tool runs on Python 3.

To create a new puzzle, run the editor like so:

    ./edit_puzzle.py

To edit an existing KenKen file (filename extension `.kk`),
load the file like so:

    ./edit_puzzle.py my_puzzle.kk

By the way, then `.kk` file format is just a JSON object
with a certain schema. Feel free to examine the files, and
even to edit them if you understand the schema, which I've
tried to keep simple

### Keyboard shortcuts

I've modeled the editing interface on vim's most common keyboard
shortcuts. So if you're familiar with vim, this will feel easy for you.
If, however, you don't like vim, then, sorry about that! But still,
it's fun to use once you have a little practice.

Here are the keyboard shortcuts:


                   --== Keyboard shortcuts ==--
    ____________________________________________________________

        hjkl Move the cursor. Wrap-around possible.
        HJKL Join or split a group via this movement.
        gg   Jump to the top-left of the puzzle.
        p    Save a pdf file of this puzzle (no solution).
        \p   Save a pdf file that includes the solution.
        o    Save the puzzle to a pdf and open the pdf file.
        e    Run the experimental puzzle solver.
        f    Find the solution to the given puzzle.
        c    Start editing clues at the current group.
        s    Set the puzzle size.
        w    Type a filename, this puzzle is saved to that file.
        \w   Save to a file, choosing a default name if needed.
        q    Quit.
        ?    See the help screen.

## Some old notes

(So far this is just a small note for myself.)

* As of 203.2021, I have a "next up" list here:
- [ ] Implment a method to eliminate known-bad grp_options in solver.py.
      See `solver.py` for a bit more on that.

I sometimes store a _set_ in `grp_options`, but I don't think this is correct
because we can have duplicates in a group. I think they should always be lists,
sorted for standardization. They could alternatively be tuples:
- [x] Update `solver.py` to ensure that number lists in `grp_options` are lists
      or tuples, never sets.

- [ ] When using the experimental solver, print out axis labels so that I can
      more easily understand the algebraic notation in the output (eg "a4=4").

___

* I have a note in the Notes app called "KenKen methods of deduction and ideas"
  which is currently the central place for my thoughts on this repo.

- [x] Saving to something with .kk doesn't add a new .kk extension.
- [ ] Be able to resize the terminal.
- [ ] Make it visually more globally obvious when we're in clue-editing mode.
- [ ] When asking for a solution handle edge cases:
  + [ ] Complain if we have an incomplete puzzle (not all clues given).
  + [ ] Give a message if no solutions.
  + [ ] Give a solution and a message if multiple solutions.
- [ ] For the auto-chosen filename, ensure it won't erase an existing file.
- [x] Make the status msg fade to dark gray over time. Thus a repeat of the same
      message (eg "saved to FILENAME") can still be understood as happening.
- [x] Right now typing 'w' and then hitting esc can cause a crash.

- [x] In clue-editing: hjkl goes to the next clueless group in that dir.
- [x] In clue-editing: n goes to the next clueless group in reading order.
- [x] If someone executes ":w" alone, it saves to the current filename.
- [x] Print out the time it took to solve a puzzle.

Eventually:
- [ ] Think about how to avoid losing data by closing a puzzle before saving.
      We could either save automatically all the time, or present a warning if
      they haven't saved yet. I'm leaning toward auto-saving.
- [ ] Update the save system to avoid overwriting files (unless we're sure the
      save is an udpate to the version on disk).
- [ ] In clue editing, accept a/s/m/d keys for clue completion.
- [ ] Don't insta-crash if the terminal isn't big enough.
      Maybe just show the biggest we can show.
- [ ] Don't crash if I hit 'n' on an empty clue in clue-entering mode.

I'm thinking about a puzzle-editing mode that has different controls from
puzzle-solving mode. The bad part about that is that it's a more complex mental
model for the user. But the challenge I'm trying to figure out is how to keep
the key-bindings vim-similar while still allowing all three of these types of
movements:

* Basic cursor movement (currently hjkl).
* Group join/split (currently HJKL).
* Jump to adjacent group by direction (currently not implemented).

That last movement feels natural as soon as I'm thinking about solving a puzzle.
It's also similar to what the hjkl keys currently do in clue-editing mode (which
again adds some complexity to the user's mental model).

## Farther in the future

- [ ] Add a keyboard-shortcut quick ref, and a help system / manual.
