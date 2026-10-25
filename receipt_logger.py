# Velvet Receipts — POSIX cooperative append transactions, unchanged JSONL hashes.
import fcntl
import hashlib
import json
import os
import threading
from contextlib import contextmanager

_lock = threading.RLock()
GENESIS_HASH = '0' * 64
_MAX_RECORD_BYTES = 16 * 1024 * 1024
_CANONICAL = ('receipt_id','timestamp','event','decision','result','policy','authorized_by','context','constraints','previous_hash')
_OPTIONAL = ('notes','confidence','domain')


class ReceiptLedgerError(RuntimeError):
    """Ledger evidence is damaged, unavailable, or not durably committed."""


class ReceiptLogger:
    """Cooperative local POSIX ledger. All readers/writers lock the ledger inode.

    Append holds LOCK_EX through full streaming validation, tail selection, hash,
    append, flush and fsync. Verification/snapshots hold LOCK_SH. Damaged or partial
    records are retained and block writes. Rotation/replacement during access and
    network filesystems are unsupported; all participating processes must use this
    protocol. Validation costs O(N) time but does not materialize the full ledger.
    """
    def __init__(self, filepath='receipts.log'):
        self.filepath = os.path.abspath(os.fspath(filepath))

    @contextmanager
    def _handle(self, write=False):
        flags = (os.O_RDWR | os.O_CREAT | os.O_APPEND) if write else os.O_RDONLY
        flags |= getattr(os, 'O_NOFOLLOW', 0)
        with _lock:
            try:
                fd = os.open(self.filepath, flags, 0o600)
            except FileNotFoundError:
                if write: raise
                yield None
                return
            with os.fdopen(fd, 'a+b' if write else 'rb') as handle:
                fcntl.flock(fd, fcntl.LOCK_EX if write else fcntl.LOCK_SH)
                try:
                    actual, named = os.fstat(fd), os.stat(self.filepath, follow_symlinks=False)
                    if (actual.st_dev, actual.st_ino) != (named.st_dev, named.st_ino):
                        raise ReceiptLedgerError('ledger was replaced during lock acquisition')
                    yield handle
                finally:
                    fcntl.flock(fd, fcntl.LOCK_UN)

    def _scan(self, handle, collect=False):
        previous = GENESIS_HASH
        entries = [] if collect else None
        if handle is None: return previous, entries
        handle.seek(0)
        position = 0
        while True:
            raw = handle.readline(_MAX_RECORD_BYTES + 1)
            if not raw: break
            position += 1
            if len(raw) > _MAX_RECORD_BYTES or not raw.endswith(b'\n'):
                raise ReceiptLedgerError('partial or oversized receipt at line %s; evidence preserved' % position)
            if not raw.strip(): continue
            try:
                entry = json.loads(raw.decode('utf-8'))
                if not isinstance(entry, dict): raise ValueError('receipt must be an object')
                payload = {k: entry[k] for k in _CANONICAL if k in entry}
                payload.update({k: entry[k] for k in _OPTIONAL if k in entry})
                computed = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
                if entry.get('hash') != computed: raise ValueError('hash mismatch')
                if entry.get('previous_hash') != previous: raise ValueError('previous_hash mismatch')
            except (ValueError, TypeError, UnicodeDecodeError) as exc:
                raise ReceiptLedgerError('invalid receipt at line %s: %s; evidence preserved' % (position, exc)) from exc
            previous = computed
            if collect: entries.append(entry)
        return previous, entries

    def read_entries(self):
        """Return one fully verified snapshot while holding the shared lock."""
        with self._handle() as handle:
            return self._scan(handle, collect=True)[1]

    def _load_entries(self):
        return self.read_entries()

    def get_last_hash(self):
        with self._handle() as handle:
            return self._scan(handle)[0]

    def log(self, receipt):
        with self._handle(write=True) as handle:
            tail, _ = self._scan(handle)
            receipt.previous_hash = tail
            receipt.hash = receipt.compute_hash()
            encoded = (json.dumps(receipt.to_dict(), sort_keys=True) + '\n').encode('utf-8')
            if len(encoded) > _MAX_RECORD_BYTES:
                raise ReceiptLedgerError('receipt exceeds 16 MiB record limit')
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
            # Persist directory entry too, including a newly created ledger.
            directory = os.open(os.path.dirname(self.filepath), os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
            try: os.fsync(directory)
            finally: os.close(directory)
        return receipt

    def verify_chain(self):
        try:
            with self._handle() as handle: self._scan(handle)
        except (OSError, ReceiptLedgerError) as exc:
            return False, [str(exc)]
        return True, []
