"""Disposable multiprocess and crash-damage regressions, no production ledger."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from receipt import Receipt
from receipt_logger import ReceiptLogger

ROOT = Path(__file__).resolve().parents[1]


def receipt():
    return Receipt('SYNTHETIC', 'observe', 'none', 'test', 'test')


class ProcessIntegrityTests(unittest.TestCase):
    def worker(self, directory, index, count=1, barrier=False):
        source = '''import sys,time,pathlib
from receipt import Receipt
from receipt_logger import ReceiptLogger
p=pathlib.Path(sys.argv[1]); i=sys.argv[2]; count=int(sys.argv[3]); barrier=sys.argv[4]=='1'
log=ReceiptLogger(str(p/'ledger.jsonl'))
if barrier:
 original=log.get_last_hash
 def synchronized_tail():
  tail=original(); (p/('ready-'+i)).write_text('1'); end=time.monotonic()+5
  while len(list(p.glob('ready-*')))<4:
   if time.monotonic()>end:raise RuntimeError('barrier timeout')
   time.sleep(.005)
  return tail
 log.get_last_hash=synchronized_tail
for _ in range(count):log.log(Receipt('SYNTHETIC','observe','none','test','test'))
'''
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(ROOT))
        return subprocess.Popen([sys.executable,'-c',source,directory,str(index),str(count),str(int(barrier))],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)

    def test_same_tail_interleaving_cannot_fork_chain(self):
        with tempfile.TemporaryDirectory() as d:
            workers=[self.worker(d,i,barrier=True) for i in range(4)]
            for w in workers:
                out,err=w.communicate(timeout=10);self.assertEqual(w.returncode,0,out+err)
            self.assertEqual(ReceiptLogger(str(Path(d)/'ledger.jsonl')).verify_chain(),(True,[]))

    def test_concurrent_writers_and_verifier(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'ledger.jsonl'; logger=ReceiptLogger(str(path))
            logger.log(receipt())
            workers=[self.worker(d,i,count=15) for i in range(4)]
            while any(w.poll() is None for w in workers):
                self.assertEqual(logger.verify_chain(),(True,[]))
            for w in workers:
                out,err=w.communicate(timeout=10);self.assertEqual(w.returncode,0,out+err)
            self.assertEqual(len(path.read_text().splitlines()),61)
            self.assertEqual(logger.verify_chain(),(True,[]))

    def test_partial_trailing_record_is_preserved_and_blocks_append_after_restart(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'ledger.jsonl';ReceiptLogger(str(path)).log(receipt())
            with path.open('ab') as h:h.write(b'{"interrupted":');h.flush();os.fsync(h.fileno())
            before=path.read_bytes()
            try: valid,_=ReceiptLogger(str(path)).verify_chain()
            except Exception: valid=False
            self.assertFalse(valid)
            with self.assertRaises(Exception):ReceiptLogger(str(path)).log(receipt())
            self.assertEqual(path.read_bytes(),before)

    def test_corrupt_history_blocks_append_without_rewriting_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'ledger.jsonl';log=ReceiptLogger(str(path));log.log(receipt())
            row=json.loads(path.read_text());row['result']='tampered';path.write_text(json.dumps(row)+'\n')
            before=path.read_bytes()
            with self.assertRaises(Exception):log.log(receipt())
            self.assertEqual(path.read_bytes(),before)

    def test_killed_writer_releases_lock_and_partial_evidence_survives(self):
        import time
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'ledger.jsonl';ReceiptLogger(str(path)).log(receipt())
            ready=Path(d)/'ready'
            child="import os,fcntl,sys,time; f=open(sys.argv[1],'ab'); fcntl.flock(f,fcntl.LOCK_EX); f.write(bytes([123])); f.flush(); os.fsync(f.fileno()); open(sys.argv[2],'w').close(); time.sleep(30)"
            worker=subprocess.Popen([sys.executable,'-c',child,str(path),str(ready)])
            try:
                deadline=time.monotonic()+5
                while not ready.exists():
                    self.assertIsNone(worker.poll())
                    if time.monotonic()>deadline:self.fail('writer did not acquire lock')
                    time.sleep(.005)
                worker.kill();worker.wait(timeout=5)
                before=path.read_bytes()
                with self.assertRaises(Exception):ReceiptLogger(str(path)).log(receipt())
                self.assertEqual(path.read_bytes(),before)
                self.assertFalse(ReceiptLogger(str(path)).verify_chain()[0])
            finally:
                if worker.poll() is None: worker.kill();worker.wait(timeout=5)


if __name__=='__main__':unittest.main()
