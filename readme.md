(So far this is just a small note for myself.)

* I have a note in the Notes app called "KenKen methods of deduction and ideas"
  which is currently the central place for my thoughts on this repo.

- [ ] Saving to something with .kk doesn't add a new .kk extension.
- [ ] Be able to resize the terminal.
- [ ] Make it visually more globally obvious when we're in clue-editing mode.
- [ ] When asking for a solution handle edge cases:
  + [ ] Complain if we have an incomplete puzzle (not all clues given).
  + [ ] Give a message if no solutions.
  + [ ] Give a solution and a message if multiple solutions.
- [ ] For the auto-chosen filename, ensure it won't erase an existing file.
- [ ] Make the status msg fade to dark gray over time. Thus a repeat of the same
      message (eg "saved to FILENAME") can still be understood as happening.

- [x] In clue-editing: hjkl goes to the next clueless group in that dir.
- [x] In clue-editing: n goes to the next clueless group in reading order.
- [x] If someone executes ":w" alone, it saves to the current filename.
- [ ] Print out the time it took to solve a puzzle.

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
