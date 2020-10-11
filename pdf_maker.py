""" pdf_maker.py

    Create pdf files based on puzzles.
"""


# ______________________________________________________________________
# Imports

import fpdf


# ______________________________________________________________________
# Internal functions

def add_line(pdf, pt1, pt2, width, offset=(0, 0)):

    w = abs(pt2[0] - pt1[0]) + width
    h = abs(pt2[1] - pt1[1]) + width

    x0 = pt1[0] - width / 2 + offset[0]
    y0 = pt1[1] - width / 2 + offset[1]

    pdf.rect(x0, y0, w, h, 'F')


# ______________________________________________________________________
# Public functions

def make_pdf(puzzle, filename):

    page_width = 215.9
    # page_width = fpdf.fpdf.PAGE_FORMATS['letter'][0]

    pdf = fpdf.FPDF('P', 'mm', 'Letter')

    pdf.add_font('NotoSans', style='', fname='NotoSans-Regular.ttf', uni=True)
    pdf.add_font('NotoSans', style='B', fname='NotoSans-Bold.ttf', uni=True)

    # pdf.set_doc_option('core_fonts_encoding', 'utf-8')
    pdf.add_page()

    lane_width = 10
    max_pt = puzzle.size * lane_width

    # Calculate where we belong on the page to be centered.
    puzzle_width = max_pt
    x0 = (page_width - puzzle_width) / 2
    y0 = 50

    # x0, y0 = 50, 50

    thick_width = 0.7
    thin_width  = 0.1

    light_color = 170

    pdf.set_fill_color(light_color)
    for i in range(1, puzzle.size):
        c = i * lane_width
        add_line(pdf, (0, c), (max_pt, c), thin_width, offset=(x0, y0))
        add_line(pdf, (c, 0), (c, max_pt), thin_width, offset=(x0, y0))

    pdf.set_fill_color(0)
    for x in range(puzzle.size):
        for y in range(puzzle.size):

            # Draw the vertical cell border.
            if x > 0 and not puzzle.are_grouped((x - 1, y), (x, y)):
                add_line(
                        pdf,
                        (x * lane_width, y * lane_width),
                        (x * lane_width, (y + 1) * lane_width),
                        thick_width,
                        offset=(x0, y0)
                )

            # Draw the horizontal cell border.
            if y > 0 and not puzzle.are_grouped((x, y - 1), (x, y)):
                add_line(
                        pdf,
                        (x * lane_width, y * lane_width),
                        ((x + 1) * lane_width, y * lane_width),
                        thick_width,
                        offset=(x0, y0)
                )

    # XXX
    for i in [0, puzzle.size]:
        c = i * lane_width
        add_line(pdf, (0, c), (max_pt, c), thick_width, offset=(x0, y0))
        add_line(pdf, (c, 0), (c, max_pt), thick_width, offset=(x0, y0))

    # TODO: How could I programmatically determine the offsets for the text?
    #       I'm not even sure if it's possible.

    # pdf.set_text_color(light_color)
    # pdf.set_font('Helvetica', 'B', 7)
    pdf.set_font('NotoSans', 'B', 7)

    for group in puzzle.groups:
        clue = group[0]
        clue_pt = puzzle.get_clue_point(group)
        pdf.set_xy(
                x0 + clue_pt[0] * lane_width,
                y0 + clue_pt[1] * lane_width
        )
        if clue[-1] in puzzle.op_chars:
            prefix, suffix = clue[:-1], clue[-1]
        else:
            prefix, suffix = clue, ''
        pdf.set_font('NotoSans', 'B', 7)
        w = pdf.get_string_width(prefix)
        pdf.cell(w + 0.01, 4.12, prefix)
        if suffix:
            pdf.set_font('NotoSans', 'B', 9)
            h = 3.7 if suffix == puzzle.sub_char else 4.2
            pdf.write(h, suffix)

            # pdf.set_font('NotoSans', '', 7)
            # pdf.set_font('Helvetica', '', 7)
            # pdf.write(3.69, suffix)
            # pdf.write(4.12, suffix)
            # pdf.cell(0, 3.69, suffix)

    pdf.output(filename, 'F')
