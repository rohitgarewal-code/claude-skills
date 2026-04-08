# Calibration Examples

Use this file to anchor evaluator strictness and avoid score inflation.

## Calibration Rules

- `7` means ship-worthy, not impressive-for-AI
- `8` means clearly strong
- `9` or `10` should be rare
- A page can be visually attractive and still fail on intent match
- A page can be highly functional and still fail on originality

## Example Anchors

### Example A — Generic But Competent

- Intent Match: 6
- Design Quality: 5
- Originality: 3
- Craft: 7
- Functionality: 7

Interpretation:
- technically solid
- too generic to ship as premium custom work
- should iterate

### Example B — Strong But Not Final

- Intent Match: 7
- Design Quality: 7
- Originality: 6
- Craft: 7
- Functionality: 8

Interpretation:
- usable and fairly polished
- still lacks enough authorship to be an excellent custom outcome

### Example C — Pass

- Intent Match: 8
- Design Quality: 8
- Originality: 7
- Craft: 8
- Functionality: 8

Interpretation:
- clearly on brief
- distinct enough to ship
- no failed hard gates

### Example D — Beautiful But Off-Brief

- Intent Match: 5
- Design Quality: 8
- Originality: 8
- Craft: 8
- Functionality: 7

Interpretation:
- evaluator should fail this
- aesthetic strength does not override a bad reading of the brief
