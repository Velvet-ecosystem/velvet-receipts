# Receipt ledger transactions and recovery

JSONL canonical payloads, SHA-256 chaining and receipt identifiers are unchanged.
Cooperating local POSIX writers now hold an exclusive flock on the ledger inode
through streaming validation, tail selection, append, flush and fsync. Snapshot
readers/verifiers hold a shared lock. read_entries() returns a verified snapshot
under one lock; Runtime consumers should use it instead of verify-then-raw-read.

No ledger content is repaired automatically. Invalid hashes, malformed JSON,
partial trailing records or missing newline refuse further append and preserve
all bytes. A killed process releases its OS lock; restart validates what remains.
A fully durable record is retained; a partial record requires operator recovery
from preserved evidence/backup into a separately reviewed ledger. Never truncate
or skip damaged evidence to make the system appear healthy. An fsync/I/O error is
an uncertain write outcome; callers must reconcile receipt IDs before retrying.

All participants must use this locking protocol on the same inode. File rotation,
unlink/replacement during use, network filesystems, hostile noncooperating writers
and Windows are not supported ownership models. Readers must not copy the raw
file during a write and treat a partial copy as a committed snapshot. Directory
entries and records are fsynced; hardware/filesystem durability still needs bench
power-loss acceptance. No claim of multi-host or adversarial filesystem safety.

Validation now streams one record at a time (16 MiB maximum per record), rather
than loading the entire ledger for every append. Append still costs O(N) to verify
history; checkpointed rotation/indexing is separate future work, not silently
claimed fixed. Existing well-formed newline-terminated histories need no migration.
A previously oversized or unterminated history now refuses operations explicitly.
