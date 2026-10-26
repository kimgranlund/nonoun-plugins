"""Compatibility across the CLI and runtime-harness updates."""
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from diagnostics import diagnose, lookup_request, single_lookup, validate_diagnostics

class ReconciliationTests(unittest.TestCase):
    def test_legacy_argument_forms(self):
        for value in ['cat pkg/missing.md', {'arguments':'cat pkg/missing.md'}, {'cmd':'cat pkg/missing.md'}]:
            self.assertEqual(lookup_request(value), ['pkg/missing.md'])
            self.assertTrue(single_lookup(value))

    def test_generic_failure_owned_only_by_single_reader(self):
        for cmd,expected in [('cat pkg/missing.md',1),('cat a b',0),('cat a; cp b c',0),('cat a | head',0),('cat $PATH',0),('cat > a',0)]:
            call=dict(id='c',seq=0,kind='call',exposures=[],evidence=dict(traceLine=1,text=json.dumps({'cmd':cmd})))
            result=dict(id='r',seq=1,kind='result',exposures=[],evidence=dict(traceLine=2,text='No such file or directory'),toolCalls=[dict(arguments=json.dumps({'cmd':cmd}),output='No such file or directory',outcome='failed')])
            d=diagnose(dict(events=[call,result],sources=[],links=[{'from':'c','to':'r'}]))
            self.assertEqual(len(d['diagnostics']['findings']),expected,cmd)
            validate_diagnostics(d)
            if expected:self.assertEqual(d['diagnostics']['findings'][0]['triage']['state'],'needs-review')

    def test_new_lookup_parser_retains_benign_triage(self):
        event=dict(id='r',seq=0,kind='result',exposures=[],evidence=dict(traceLine=1,text=json.dumps({'output':'Warning: truncated output\nRequired answer returned; omitted optional debug footer'})))
        d=diagnose(dict(events=[event],sources=[],links=[]))
        self.assertEqual(d['diagnostics']['findings'][0]['triage']['state'],'likely-benign')
        validate_diagnostics(d)
