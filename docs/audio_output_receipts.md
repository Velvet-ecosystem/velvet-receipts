# Audio Output Receipts

Velvet Receipts normalizes accepted Audio Studio output evidence into the canonical append-only receipt chain.

Supported evidence events:

- `audio.output.booked`
- `audio.output.started`
- `audio.output.completed`
- `audio.output.preempted`
- `audio.output.failed`
- `audio.output.recovered`

The source Event Protocol contract is `velvet.audio-output-evidence.v1`. The canonical receipt context schema is `velvet.receipts.audio-output.v1`.

## Evidence boundary

These receipts record operational facts about the audio organ: request identity, node, priority, logical output channels, delivery profile/model identifiers, sample rates, frames, duration, preemption relationships, and bounded failure/recovery details.

They deliberately do not copy:

- the spoken sentence
- transcripts
- PCM or other raw audio
- ALSA device paths
- voice-model filesystem paths
- capability, Court, or execution tokens
- authority or actuation claims

The `authorized_by` field uses `AudioStudioEvidencePath` as the recorder identity required by the shared Receipt model. It is not a claim that Audio Studio authorized the speech or any physical action.

## Receipt meanings

- booking receipt: a Studio output lease was recorded
- start receipt: playback began through the accepted local path
- completion receipt: playback finished with measured frame/duration evidence
- preemption receipt: a lower-priority output was displaced by a named higher-priority request
- failure receipt: synthesis, booking, or playback failed and requires recovery
- recovery receipt: a later successful output demonstrated recovery from the recorded failure

A Runtime ingress acknowledgement and a canonical Velvet receipt answer different questions. The ingress acknowledgement proves durable Runtime acceptance of the event. The Velvet receipt proves that evidence was normalized into the canonical append-only chain.

Neither receipt grants authority.
