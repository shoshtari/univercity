# University of Tehran proposal template

This folder contains an editable XeLaTeX recreation of the supplied University of Tehran proposal form.
The sample proposal's subject matter is not copied; only the reusable visual structure is reproduced.

## Compile

From this directory, run:

```sh
latexmk -xelatex proposal.tex
```

The template uses the bundled `Vazirmatn Regular` for Persian body text and
`Vazirmatn Bold` for headings and emphasis. The fonts in `assets/fonts/` are from
[Vazirmatn v33.003](https://github.com/rastikerdar/vazirmatn/tree/v33.003), with their
SIL Open Font License included in `assets/fonts/OFL.txt`.
It uses `Times New Roman` for Latin text, with `TeX Gyre Termes` as a fallback.

## Customize

1. Edit the commands under `EDITABLE FIELDS` near the top of `proposal.tex`.
2. Replace the gray demonstration paragraphs with your proposal text.
3. Use `UTProposalSection` for additional blue-bordered sections. It automatically continues across pages.
4. Change `UTCheckedBox` to `UTBox`, or vice versa, for form choices.
5. Enter the reference number in `ProposalReferencePartA` through `ProposalReferencePartD`; these map to the four boxes on the original cover.

The document is set to US Letter because the supplied university PDF is 612 x 792 points.
