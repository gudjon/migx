# Discovery learning memory (Migx)

SSoT for **customer** evidence and product-discovery events lives here (or as federation signals
until files are added). Technical EVDs stay under dossier `results/`.

## How to add evidence

Prefer one markdown file per capture:

`kanban/discovery/YYYY-MM-DD-<slug>.md`

Minimum fields (from DC-PDCL domain events):

```yaml
event: CustomerEvidenceCaptured  # or OpportunityFormed | AssumptionDeclared | ...
segment: ""
context: ""
evidence_type: past_behavior  # not compliment | hypothetical
method: interview | observation | win_loss | usage
confidence: low | medium | high
implication: ""
links: []
```

Full operating map: `kanban/knowledge/product-discovery-customer-leadership-migx.md`
