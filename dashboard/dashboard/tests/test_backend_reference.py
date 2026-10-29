"""T22: pure-function snapshots only; never connects to AWS or the real database."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent / 'backend_reference'
def load(name):
    spec=importlib.util.spec_from_file_location('reference_'+name, ROOT/(name+'.py'))
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
chain=load('hash_chain'); risk=load('risk')

class BackendReferenceTests(unittest.TestCase):
    def rows(self):
        rows=[];previous=chain.GENESIS_HASH
        for i,humidity in enumerate([55.5,68.4,70.4],1):
            args=('fixture-sensor','2026-10-28T12:00:%02dZ'%i,20.1,humidity)
            digest=chain.calculate_hash(previous,*args)
            rows.append((i,*args,previous,digest));previous=digest
        return rows
    def test_backend_risk_boundaries_match_the_display_logic(self):
        for humidity,want in [(0,'LOW'),(60,'LOW'),(60.1,'MODERATE'),(70,'MODERATE'),(70.4,'HIGH'),(100,'HIGH')]:
            self.assertEqual(risk.risk_level(humidity),want)
    def test_unchanged_chain_is_verified(self):
        self.assertEqual(chain.verify_chain(self.rows()),{'status':'OK','checked':3})
    def test_changed_humidity_is_detected_without_touching_real_data(self):
        rows=self.rows();changed=list(rows[1]);changed[4]=95.5;rows[1]=tuple(changed)
        result=chain.verify_chain(rows);self.assertEqual(result['status'],'Tampered');self.assertEqual(result['first_bad_id'],2)
    def test_broken_link_is_detected(self):
        rows=self.rows();changed=list(rows[2]);changed[5]='0'*64;rows[2]=tuple(changed)
        self.assertEqual(chain.verify_chain(rows)['first_bad_id'],3)
    def test_empty_chain_is_not_evidence_of_any_verified_readings(self):
        self.assertEqual(chain.verify_chain([]),{'status':'OK','checked':0})
