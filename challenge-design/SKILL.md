---
name: challenge-design
description: Pressure-test a major design with a live debate. A defender and a challenger agent message each other directly, agree a framework and a topic list, then work topic by topic until 90%+ of topics are aligned, every topic is aligned, or an hour is up. Reports what they aligned on and what they could not.
allowed-tools: Agent, Task, SendMessage, Bash, Read, Write, Glob, Grep
---

# Design Challenge

Two agents argue a design out **with each other**, not past each other. The **defender** presents
the design and holds the ledger. The **challenger** goes through it point by point and proposes
what would be better. They first agree **how** they will judge the design, then work through every
topic until they align on a resolution or show they can't. You (the orchestrator) keep the clock
and the rules, then report back. You do not pick a winner; the human decides whatever stays open.

## When to invoke

- After creating or proposing a major design (architecture, data model, API shape, workflow)
- Before committing to an architecture or data model, or when choosing between approaches
- Manually: `/challenge-design [design doc or topic] [--minutes N] [--target P]`
  (defaults: 60 minutes, 90% target)

## 1. Prepare the brief (the defender can only defend what it's given)

1. Identify the design: `$ARGUMENTS`, or the most recent design/plan in the conversation.
2. Make a working folder: `<scratchpad>/challenge-<slug>/` (or `/tmp/challenge-<slug>/` with no
   scratchpad). Write `design.md` there with:
   - **The design in full.** Link or paste the design doc; never a 2–3 sentence summary.
   - **Why it is this way.** Goals, constraints and rejected alternatives from the conversation.
     Without the reasons, the defender caves on the first plausible objection.
   - **Locked decisions.** Anything the human already decided. The pair may recommend reopening
     one, but it can't be aligned away. It goes in the report as a question for the human.
   - **Files to read.** The code, schemas and docs the design touches.
3. Record the clock: `date -u +%Y-%m-%dT%H:%M:%SZ` gives START, and DEADLINE = START + minutes.

## 2. Start the debate

Agents cannot see their own IDs, but they can message any agent whose ID they're given, and
they can always reply to whoever messaged them. An agent that has finished its turn wakes up
when a message arrives. So the agents talk directly, and you only start and end the debate.

1. Spawn the **challenger** first (background, `general-purpose`) with the challenger prompt
   below. It reads the design and code, then waits for the defender's presentation.
2. Spawn the **defender** (background, `general-purpose`) with the defender prompt below,
   including the challenger's agent ID from step 1.
3. `SendMessage` the challenger the defender's agent ID, so either side can start a message.
4. Start the timer: background Bash `sleep <minutes*60>; echo CHALLENGE_TIME_UP`. Its completion
   notification is your cue to call time.

If your Agent tool takes a `name`, name them `defender` and `challenger`, and use the names as
addresses instead of IDs.

**While it runs:** each agent's turn ends and resumes many times. Those completion
notifications are normal, so don't report from them. Don't argue, don't relay, and don't
summarise to the human mid-run. Step in only if:

- **The timer fires.** Message both: "TIME. Close now: defender sends FINAL LEDGER within 5 minutes."
- **Neither agent has done anything for 15 minutes.** Nudge both with the ledger path.
- **Messages between the agents fail.** Switch to relay mode: forward each message word for word
  between the two, with the same protocol. You are a pipe, not a participant.

## 3. The protocol (put this whole block in BOTH prompts)

```
RULES OF ENGAGEMENT
Brief: <path>/design.md   Ledger: <path>/ledger.md (the defender writes it; the challenger reads it)
Deadline: <DEADLINE UTC>. Check `date -u` before every message; at the deadline, close.
Talk only through SendMessage. Your plain output is invisible to the other agent.
Start every message with one self-contained line: "[T<n>|phase] <what this message does>".

PHASE 0, READ. Read the brief and every file it names. Claims need evidence: a file and line,
a measurement, a documented constraint. No armchair arguments.

PHASE 1, PRESENT (defender). Send the design as a numbered list of its decisions, each with its why.

PHASE 2, FRAMEWORK. Before arguing any merits, agree on:
  (a) Criteria and their priority. Start from correctness, simplicity, reliability/operability,
      extensibility, performance/cost and developer experience, plus the project's own principles
      (its CLAUDE.md, charter, or a design doc it points to).
  (b) The topic list. One topic per design decision or challenge point. The challenger must get
      every one of its challenges onto the list. If ~/.claude/skills/jev-fit/SKILL.md exists,
      "Jev fit" is always a topic, and the challenger checks the design's Jev fit table against
      that skill.
  (c) What counts as evidence, and what a resolution looks like: KEEP as designed, CHANGE to a
      concrete alternative, or HYBRID (which parts from each, precisely).
  The defender writes the agreed framework and topic list to the ledger. From then on the list
  is FROZEN: topics can be added or split, never dropped or merged away. Every topic counts.

PHASE 3, TOPICS. For each topic: the challenger states the critique and a CONCRETE alternative
(implementable, not "consider X"). The defender accepts, counters, or proposes a hybrid. Go back
and forth. Several topics may run in one message.
  ALIGNED = one side sends "PROPOSE T<n>: <one-sentence resolution>" and the other replies
            "AGREE T<n>" to that exact wording. The defender records the resolution, its basis
            (evidence | constraint | trade-off | deferral) and whether it changes the design.
  DEADLOCKED = two exchanges in a row where neither position moved. Record both positions in a
            sentence each, plus what would settle it (a measurement, a prototype, a human call).
            Revisit deadlocked topics if time is left.

HONEST ALIGNMENT. The target is a better design, not a percentage.
  - Concede only for a reason you can state: evidence, a constraint you missed, a better
    trade-off. "To reach agreement" is not a reason.
  - An alignment you can't justify is worse than an honest deadlock. Mark it basis=deferral and
    it is flagged to the human.
  - Steel-man: before you counter, restate the other side's strongest point in one line.
  - A locked decision can't be aligned away. Record "recommend reopening" and move on.

PHASE 4, CLOSE when any of these holds:
  - every topic is ALIGNED;
  - at least <target>% are ALIGNED and every remaining topic is DEADLOCKED;
  - the deadline has passed.
  The defender sends the orchestrator ("main") "FINAL LEDGER" plus the ledger contents. The
  challenger sends main "LEDGER CONFIRMED", or lists the entries it disputes. Then both stop.
```

## 4. The prompts

**Challenger** (spawn first):
```
You are the CHALLENGER of a design. Your job: go through every decision in it, say what would be
done better, and propose concrete alternatives, then argue each one to alignment with the
defender. Read the brief and the code now. When you've read everything, end your turn; the
defender's presentation will arrive as a message. Reply to the defender through SendMessage
(reply to whoever messaged you). Push hard where the evidence supports it, and concede where it
doesn't.
<RULES OF ENGAGEMENT block>
```

**Defender** (spawn second):
```
You are the DEFENDER of a design. You present it, then defend it point by point against the
challenger (agent ID <challenger id>). You hold the ledger at <path>/ledger.md and keep it
current after every resolved or deadlocked topic. Defend what the evidence supports, and adopt
the challenger's alternative where it is genuinely better. The goal is the best design, not the
original one. Read the brief and the code, then send your presentation (Phase 1) to the
challenger.
<RULES OF ENGAGEMENT block>
```

Ledger format (the defender keeps it):
```
# Challenge ledger: <design>   (deadline <UTC>)
Framework: <criteria in priority order> · evidence: <...>
| # | Topic | Status | Resolution (agreed wording) | Changes design? | Basis |
Deadlocked: T<n>: defender <...> / challenger <...> / settle by <...>
```

## 5. Report to the human

When both close-out messages are in (or 5 minutes after you call time), read the ledger and report:

```
## Design challenge: <design>
Aligned on <a> of <n> topics (<pct>%) · stopped because <all aligned | target met, rest
deadlocked | time> · <minutes> min

### What they aligned on
| # | Topic | Resolution | Changes the design? | Basis |

### What they could not align on
| # | Topic | Defender's position | Challenger's position | What would settle it |

### The design after alignment
<numbered list of the changes to the original design; "unchanged" items need no line>

### Flags
<alignments by deferral · locked decisions recommended for reopening · disputed ledger entries>
```

End with: "Want me to update the design with the aligned changes? The open items are your call."

## Important

- **Real dialogue or nothing.** If the agents never exchanged messages, say so, and treat the
  result as two monologues.
- **Every topic counts.** The percentage is aligned topics divided by the frozen list, including
  added topics. Never shrink the denominator.
- **Neutral orchestrator.** You report their alignment. You add no verdict of your own, beyond
  flagging deferrals and disputes.
- **Budget.** Two agents for up to an hour is real spend. Use `--minutes` to shorten it for
  smaller designs.
