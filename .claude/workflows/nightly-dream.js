export const meta = {
  name: 'nightly-dream',
  description:
    'The Migx autonomous improvement cadence (the Dream). Delta-only (bounded by the git watermark), ' +
    'anti-stall: SENSE the drift since last run across 5 tiers, VERIFY refute-by-default, ACT ' +
    '(mechanical fixes -> a PR-shaped branch; judgment calls -> kanban/tasks/ cards), REPORT + advance ' +
    'the watermark. Prunes stale memory as well as adding. See kanban/playbook/04.',
  phases: [{ title: 'Sense' }, { title: 'Verify' }, { title: 'Act' }, { title: 'Report' }],
};

const WATERMARK = 'kanban/triggers/dream-watermark.json';
const REPO = 'Migx (Mixxx fork, C++/Qt6/CMake). Harness: kanban/AGENTS.md, kanban/playbook/, kanban/patterns/, kanban/architecture/.';

const FINDING_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['tier', 'converged', 'findings'],
  properties: {
    tier: { type: 'string' },
    converged: { type: 'boolean', description: 'true = no new delta since the watermark (anti-stall)' },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['summary', 'kind', 'evidence'],
        properties: {
          summary: { type: 'string' },
          kind: { type: 'string', enum: ['mechanical', 'judgment', 'prune'] },
          evidence: { type: 'string', description: 'file:line / commit / typed ID' },
        },
      },
    },
  },
};

// --- SENSE: 5 tiers, each reads only commits since the watermark ---
const TIERS = [
  ['benchmark-regression-sweep',
    'Compare current EVD-* benchmark records to their pinned baselines; flag any subsystem whose p99/max ' +
    'slipped or gained an underrun since the watermark (P-18). Clean tiers report converged:true.'],
  ['stale-pattern-prune',
    'Find pattern/antipattern cards or tasks that are now stale, contradicted by code, or unused since the ' +
    'watermark. Propose PRUNES (memory decays, not only grows). kind:prune.'],
  ['dossier-reality-grooming',
    'Reconcile OPEN dossiers against reality: planned-but-zero-merged-code, sealed-but-boilerplate-retro ' +
    '(AP-01), or claims contradicted by HEAD. kind:judgment for verdicts.'],
  ['plan-vs-merged-code-drift',
    'Diff what dossiers/PSes claimed vs what actually merged (git) since the watermark; flag drift where ' +
    'the living layer (patterns/DDD/AGENTS.md) no longer matches the code.'],
  ['upstream-mixxx-changelog-delta',
    'Scan for upstream Mixxx changes relevant to Migx since the watermark that we should track or diverge ' +
    'from deliberately (fork_delta). kind:judgment.'],
];

phase('Sense');
log(`Dream SENSE across ${TIERS.length} tiers, delta-bounded by ${WATERMARK}`);

const sensed = await parallel(
  TIERS.map(([tier, task]) => () =>
    agent(
      `${REPO}\n\nDREAM TIER: ${tier}. ${task}\n\nDELTA-ONLY: read the watermark at ${WATERMARK} and only ` +
        `consider commits since it (use git log). If there is no new delta, return converged:true with an ` +
        `empty findings list — do NOT invent work. Refute-by-default in what you surface. Return the schema.`,
      { label: `sense:${tier}`, phase: 'Sense', schema: FINDING_SCHEMA },
    ),
  ),
);

const findings = sensed
  .filter(Boolean)
  .flatMap((t) => (t.findings || []).map((f) => ({ ...f, tier: t.tier })));
log(`SENSE: ${findings.length} candidate finding(s); ${sensed.filter((t) => t && t.converged).length}/${TIERS.length} tiers converged`);

if (findings.length === 0) {
  phase('Report');
  const rpt = await agent(
    `${REPO}\n\nThe Dream found no delta this run — every tier converged. Write a one-line heartbeat entry ` +
      `to kanban/triggers/heartbeats.yaml (nightly-dream: last_run + outcome:converged) and advance the ` +
      `watermark in ${WATERMARK} to HEAD. Report the no-op.`,
    { label: 'report-converged', phase: 'Report' },
  );
  return { converged: true, findings: [], report: rpt };
}

// --- VERIFY: adversarial, refute-by-default. A finding survives only if the verifier can't refute it. ---
phase('Verify');
const verified = await pipeline(
  findings,
  (f) =>
    agent(
      `${REPO}\n\nADVERSARIALLY VERIFY this Dream finding — try to REFUTE it. Default to refuted:true if the ` +
        `evidence doesn't hold at HEAD.\nFinding: ${f.summary}\nKind: ${f.kind}\nEvidence: ${f.evidence}\n` +
        `Return {refuted: boolean, why: string}.`,
      {
        label: `verify:${f.tier}`,
        phase: 'Verify',
        schema: {
          type: 'object', additionalProperties: false, required: ['refuted', 'why'],
          properties: { refuted: { type: 'boolean' }, why: { type: 'string' } },
        },
      },
    ).then((v) => ({ ...f, verdict: v })),
);

const survivors = verified.filter((f) => f && f.verdict && !f.verdict.refuted);
log(`VERIFY: ${survivors.length}/${findings.length} finding(s) survived refutation`);

// --- ACT: mechanical/prune -> a PR-shaped worktree change; judgment -> a kanban/tasks/ card ---
phase('Act');
const acted = await parallel(
  survivors.map((f) => () => {
    if (f.kind === 'judgment') {
      return agent(
        `${REPO}\n\nThis Dream finding is a JUDGMENT call — do NOT fix it. Write a well-formed ` +
          `kanban/tasks/<slug>.md card (per kanban/tasks/AGENTS.md: authored_by: nightly-dream, ` +
          `authored_kind: agent, triggered_by, acceptance) describing it for a human to decide.\n` +
          `Finding: ${f.summary}\nEvidence: ${f.evidence}`,
        { label: `act:card:${f.tier}`, phase: 'Act' },
      ).then((r) => ({ finding: f, action: 'task-card', result: r }));
    }
    return agent(
      `${REPO}\n\nThis Dream finding is ${f.kind === 'prune' ? 'a PRUNE' : 'a MECHANICAL fix'} — apply it ` +
        `in an isolated worktree as a small, reviewable, PR-shaped change (one concern, commit with a clear ` +
        `message citing the tier). Respect house physics (P-02) and single-source-of-truth. If applying it ` +
        `turns out to need judgment, STOP and write a tasks/ card instead.\nFinding: ${f.summary}\nEvidence: ${f.evidence}`,
      { label: `act:fix:${f.tier}`, phase: 'Act', isolation: 'worktree' },
    ).then((r) => ({ finding: f, action: f.kind === 'prune' ? 'prune-pr' : 'mechanical-pr', result: r }));
  }),
);

// --- REPORT: heartbeat + advance watermark ---
phase('Report');
const report = await agent(
  `${REPO}\n\nThe Dream acted on ${acted.filter(Boolean).length} finding(s). Write the run summary, append a ` +
    `heartbeat entry to kanban/triggers/heartbeats.yaml (nightly-dream: last_run + outcome + counts), and ` +
    `advance the watermark in ${WATERMARK} to HEAD so the next run is delta-only. Do NOT advance the ` +
    `watermark if any ACT step failed to commit — report that instead.\n\nActions:\n` +
    JSON.stringify(acted.filter(Boolean).map((a) => ({ tier: a.finding.tier, action: a.action, summary: a.finding.summary })), null, 2),
  { label: 'report', phase: 'Report' },
);

return { converged: false, sensed: findings.length, survived: survivors.length, acted: acted.filter(Boolean).length, report };
