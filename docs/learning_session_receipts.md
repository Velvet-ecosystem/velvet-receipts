# Learning Mode Session Receipts

Velvet Receipts normalizes accepted `velvet.learning-session-events.v1` lifecycle events into the canonical append-only receipt chain using `velvet.receipts.learning-session.v1`.

Supported lifecycle evidence:

- `learning.session.proposed`
- `learning.session.eligibility_checked`
- `learning.session.opened`
- `learning.session.studying`
- `learning.session.review_pending`
- `learning.session.paused`
- `learning.session.degraded`
- `learning.session.insufficient_evidence`
- `learning.session.completed`
- `learning.session.aborted`

## What the receipt proves

A Learning Mode receipt proves that the accepted lifecycle event was normalized into Velvet's append-only evidence chain. It may preserve body/node binding, study-subject reference, evidence references, eligibility references, cognitive workspace references, distributed-work references, candidate references, simulated-evidence references, bounded step counts, and compact reason codes.

It does not prove that a candidate conclusion is true, that memory was promoted, that Runtime work was placed, or that any behavioral change was applied.

## Study-content boundary

The receipt family deliberately refuses raw study content. It does not copy objectives as prose, prompts, queries, web pages, Library documents, transcripts, raw media, model output, capability or Court tokens, executor handles, hardware targets, commands, or actuation claims.

The durable receipt records the shape and provenance of the study, not a second copy of the study corpus.

## Ghost boundary

Ghost remains the fake-car and simulated-vehicle fixture path. If a Learning Mode session uses Ghost-backed evidence, those evidence references remain explicitly listed in `simulated_evidence_refs`. The receipt validator requires every simulated reference to also appear in the session's ordinary evidence list.

This preserves the difference between simulated vehicle evidence and live-body evidence through the canonical receipt chain.

## Authority boundary

Learning Mode lifecycle receipts are evidence only. They cannot:

- promote candidate memory
- alter doctrine or identity
- grant Runtime placement
- grant Court authority
- execute work
- actuate hardware
- apply a learning or plasticity change

The shared Receipt model requires an `authorized_by` field. For this family it contains `LearningSessionEvidencePath`, which names the recorder/normalization path only. It is not an authorization claim.
