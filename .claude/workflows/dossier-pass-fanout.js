export const meta = {
  name: 'dossier-pass-fanout',
  description:
    'Open a Migx dossier by fanning the research / problem-statement / architecture passes across ' +
    'parallel agents, then synthesizing a plan draft. Pass the problem (and optional dossier path) as args.',
  phases: [
    { title: 'Passes' },
    { title: 'Synthesize' },
  ],
};

// args: { problem: string, dossierPath?: string, contexts?: string[] }
const problem = (args && args.problem) || String(args || '');
const dossierPath = (args && args.dossierPath) || '(new dossier — scaffold from kanban/planning/_template/)';

const COMMON =
  `Migx (Mixxx fork, C++/Qt6/CMake). Problem: ${problem}\nDossier: ${dossierPath}\n` +
  `Honor the harness: kanban/AGENTS.md (MG-1..6), .claude/rules/planning-harness.md, the pattern ` +
  `catalogue (kanban/patterns/), and the DDD map (kanban/architecture/README.md). Cite by ID; ground ` +
  `claims in real file:line at HEAD. Respect house physics (P-02/AP-02). This is the north-star ` +
  `perf initiative unless stated otherwise (initiative-apple-silicon).`;

const PASS_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['pass', 'findings'],
  properties: {
    pass: { type: 'string' },
    findings: { type: 'array', items: { type: 'string' } },
    citations: { type: 'array', items: { type: 'string' }, description: 'file:line or typed IDs' },
    open_questions: { type: 'array', items: { type: 'string' } },
  },
};

phase('Passes');

// Three independent passes. parallel() barrier so synthesis sees all three together.
const passes = await parallel([
  () =>
    agent(
      `${COMMON}\n\nRESEARCH PASS. Prior art + upstream (Mixxx) status for this problem: does the ` +
        `capability exist upstream, is it in-flight, or rejected? Known techniques and their tradeoffs ` +
        `on Apple Silicon (Qt RHI/Metal, Accelerate/vDSP, unified memory). Establish what a baseline ` +
        `benchmark would measure. Return findings + citations + open_questions.`,
      { label: 'research', phase: 'Passes', schema: PASS_SCHEMA },
    ),
  () =>
    agent(
      `${COMMON}\n\nPROBLEM-STATEMENT PASS. Draft the PS(es): one EARS sentence each + a ` +
        `machine-consumable acceptance block (numeric threshold + the exact benchmark/test that checks ` +
        `it; for perf use p99/max + zero underruns vs a pinned baseline, never a mean — P-03/P-18). ` +
        `Name the owning DDD context (arch-*). Return each PS as a findings entry.`,
      { label: 'problem-statements', phase: 'Passes', schema: PASS_SCHEMA },
    ),
  () =>
    agent(
      `${COMMON}\n\nARCHITECTURE PASS. Options considered (table: option/pros/cons/verdict), the touched ` +
        `subsystems and where they sit relative to the RT audio thread and the GPU boundary, patterns/ADRs ` +
        `cited by ID, and the verifiability gate. Flag any RT-safety or GPU-gates-audio risk (P-02/P-21/AP-02/AP-12).`,
      { label: 'architecture', phase: 'Passes', schema: PASS_SCHEMA },
    ),
]);

const good = passes.filter(Boolean);
log(`Passes complete: ${good.map((p) => p.pass).join(', ') || 'none'}`);

phase('Synthesize');

const synthesis = await agent(
  `${COMMON}\n\nSYNTHESIZE the three passes below into a dossier plan draft ready to drop into ` +
    `kanban/planning/_template/: (1) bounded scope + non-goals, (2) the closed loop (Trigger/Capture/` +
    `Intelligence/Adjustment — P-01), (3) the PS list with EARS + acceptance, (4) ordered execution ` +
    `waves each with a verifiability gate, recommending a baseline-only first wave. Reconcile ` +
    `contradictions between passes and call out unresolved open questions.\n\nPASSES:\n` +
    JSON.stringify(good, null, 2),
  { label: 'synthesis', phase: 'Synthesize' },
);

return { problem, dossierPath, passes: good, plan: synthesis };
