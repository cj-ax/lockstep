# Pipeline test, not the Slalom team's rulings

This folder exercises `review.py apply` and `generate.py` on the Slalom review before anyone has ruled.

`rulings.test.json` approves one item: the tokens, type styles and components that Figma and code already agree on. Every conflict and every missing component is left open, so nothing contested is generated, and each component page lists its open questions.

The real rulings are recorded on the review page (`learn/slalom/review/review.html`, published as a private artifact). When the team has ruled, generate again from those rulings into `learn/slalom/generated/` and delete this folder.
