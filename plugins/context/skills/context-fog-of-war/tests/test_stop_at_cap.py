"""Stop at the output token cap, read from a bundle that records outputTokens and maxTokens but no stop reason."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from bundle import ingest
from reconstruct import reconstruct

MAPPING = {'version': 1, 'rules': [{'filePattern': '*.jsonl', 'recordPath': '', 'eventType': 'model_request', 'fields': {
    'conversationId': '/conv', 'requestId': '/id', 'maxTokens': '/request/max_tokens', 'outputTokens': '/usage/outputTokens', 'stopReason': '/stop'}}]}


def detect(records):
    with tempfile.TemporaryDirectory() as t:
        Path(t, 'turns.jsonl').write_text('\n'.join(json.dumps(r) for r in records) + '\n')
        data = reconstruct(ingest(t, MAPPING))
    found = [f for f in data['diagnostics']['findings'] if f['detector'] == 'stop-at-cap']
    row = next(c for c in data['diagnostics']['coverage'] if c['detector'] == 'stop-at-cap')
    return found, row


def turn(i, output, cap=4096, **extra):
    return dict({'conv': 'c1', 'id': 'r%d' % i, 'request': {'max_tokens': cap}, 'usage': {'outputTokens': output}}, **extra)


class StopAtCap(unittest.TestCase):
    def test_equal_to_cap_is_a_candidate(self):
        found, row = detect([turn(1, 4096), turn(2, 900)])
        self.assertEqual(len(found), 1)
        self.assertIn('4096', found[0]['observation'])
        self.assertEqual(row['explanation']['eligible'], 2)

    def test_below_cap(self):
        found, row = detect([turn(1, 4095)])
        self.assertEqual(found, [])
        self.assertEqual(row['explanation']['eligible'], 1)

    def test_recorded_stop_reason_is_excluded_and_a_missing_one_is_a_gap(self):
        found, row = detect([turn(1, 4096, stop='end_turn'), turn(2, 4096)])
        self.assertEqual(found, [])
        self.assertEqual(row['explanation']['eligible'], 0)
        self.assertEqual(row['explanation']['excluded'], {'Stop reason recorded; it is the direct evidence': 1})
        self.assertEqual([g['reason'] for g in row['explanation']['gaps']], ['Stop reason missing on this request although the trace records it elsewhere'])

    def test_duplicate_request_id_is_a_gap(self):
        found, row = detect([turn(1, 4096), turn(1, 4096), turn(2, 4096)])
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]['metrics'], {'outputTokens': 4096, 'maxTokens': 4096})
        self.assertEqual(row['explanation']['eligible'], 1)
        self.assertEqual([(g['reason'], g['count']) for g in row['explanation']['gaps']], [('Duplicate or ambiguous request identity', 2)])

    def test_missing_field_abstains(self):
        found, row = detect([{'conv': 'c1', 'id': 'r1', 'usage': {'outputTokens': 4096}}])
        self.assertEqual(found, [])
        self.assertEqual(row['explanation']['eligible'], 0)


if __name__ == '__main__':
    unittest.main()
