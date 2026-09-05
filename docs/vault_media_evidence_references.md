# Vault Media Evidence References

Velvet receipts may need to prove which retained media object belonged to an event without copying the media payload into the receipt chain.

The receipt-side contract is a small immutable reference:

```json
{
  "schema": "velvet.vault.object_ref.v1",
  "object_id": "obj-example",
  "path": "media/video/retained/incident.mp4",
  "kind": "video",
  "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "retention": "PROTECTED"
}
```

## Boundary

The reference is evidence context only.

```text
vault reference present != bytes are trusted
vault reference present != retrieval is authorized
vault reference present != retention may be changed
vault reference present != filesystem access is granted
```

The referenced path is vault-relative rather than `/srv/velvet/...` absolute. This keeps receipts portable if the same vault is mounted elsewhere on another verified body.

The SHA-256 binds the receipt reference to the bytes observed by the producer at the time the reference was created. Independent verification of the file can later reveal drift or tampering.

## Minimal fields

`vault_reference.validate_vault_object_ref()` accepts only:

- `schema`
- `object_id`
- `path`
- `kind`
- `sha256`
- `retention`

Unexpected fields are rejected so camera payloads, credentials, raw private data, mount secrets, or storage-control instructions cannot quietly grow into the receipt.

## Event usage

A domain receipt may include one or more validated references in its own payload, for example:

```json
{
  "event": "SECURITY_EVENT_RETAINED",
  "result": "completed",
  "vault_object_refs": [
    {
      "schema": "velvet.vault.object_ref.v1",
      "object_id": "obj-example",
      "path": "media/video/security/event-001.mp4",
      "kind": "video",
      "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      "retention": "PROTECTED"
    }
  ]
}
```

The producer remains responsible for the domain receipt contract and for recording the strongest known truth. A later missing file does not rewrite a historical receipt into "nothing happened"; it becomes a separate storage-integrity or degraded-evidence condition.

## Retention

The receipt records the retention class observed when the reference was emitted. It does not itself change storage retention.

Vault retention policy lives with the vault owner. Current classes are:

```text
CACHE
ROLLING
STANDARD
PROTECTED
PERMANENT
```

Evidence-worthy video should normally be promoted out of `ROLLING` before or as the event is finalized, then the receipt records the resulting protected reference.

## Privacy

Do not place raw video, still images, audio, location traces, credentials, encryption material, or unnecessary private metadata directly into the receipt solely because a vault object exists.

Receipts should preserve accountability while the vault preserves the large payload.
