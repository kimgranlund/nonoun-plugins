#!/usr/bin/env python3
import sys,json,unittest,copy
sys.dont_write_bytecode=True
from native_traces import parse

def row(p,type='event_msg'):return {'type':type,'payload':p}
def fixture():return [row({'type':'message','role':'user','content':[{'text':'Build a component comparison page'}]},'response_item'),row({'type':'task_started','turn_id':'private-id'}),row({'model':'gpt-6-sol','effort':'low'},'turn_context'),row({'type':'custom_tool_call','call_id':'c','name':'exec','input':'await tools.exec_command({cmd:"cat /skills/component-variants/SKILL.md"})'},'response_item'),row({'type':'custom_tool_call_output','call_id':'c','output':'PRIVATE_MARKER'},'response_item'),row({'type':'task_complete'})]
def encoded(rows):return ('\n'.join(json.dumps(x) for x in rows)+'\n').encode()
class NativeTests(unittest.TestCase):
    def test_native_positive_and_privacy(self):
        n=parse(encoded(fixture()));t=n['turns'][0];self.assertEqual(t['category'],'candidate-real-use');self.assertTrue(t['startedAndCompleted']);self.assertEqual(t['pureSkillReadCalls'],1);self.assertEqual(t['loggedToolReturnUtf8Bytes'],len('PRIVATE_MARKER'));self.assertNotIn('PRIVATE_MARKER',json.dumps(n));self.assertNotIn('Build a',json.dumps(n));self.assertFalse(t['performanceEligible'])
    def test_catalog_mention_is_not_use(self):
        n=parse(encoded([row({'type':'message','role':'user','content':[{'text':'component-variants wireframe-review base-ui'}]},'response_item')]));self.assertEqual(n['turns'],[])
    def test_mixed_command_is_not_pure_read(self):
        r=fixture();r[3]['payload']['input']='await tools.exec_command({cmd:"cat /skills/component-variants/SKILL.md; node long-file-name.js"})';self.assertEqual(parse(encoded(r))['turns'][0]['pureSkillReadCalls'],0)
    def test_long_mixed_read_does_not_backtrack(self):
        r=fixture();r[3]['payload']['input']=json.dumps({'cmd':'cat /skills/component-variants/'+('a'*10000)+'; echo x'});self.assertEqual(parse(encoded(r))['turns'][0]['pureSkillReadCalls'],0)
    def test_duplicate_and_conflict(self):
        r=fixture();r.append(copy.deepcopy(r[4]));self.assertEqual(parse(encoded(r))['turns'][0]['pairedToolResults'],1);r[-1]['payload']['output']='different';n=parse(encoded(r));self.assertEqual(n['conflictingCallIdentities'],1);self.assertEqual(n['turns'][0]['pairedToolResults'],0)
    def test_missing_result_not_success(self):
        r=fixture();r.pop(4);n=parse(encoded(r));self.assertEqual(n['turns'][0]['missingToolResults'],1);self.assertFalse(n['turns'][0]['performanceEligible'])
    def test_turn_category_does_not_relabel_predecessor(self):
        r=fixture()+[row({'type':'message','role':'user','content':[{'text':'Now analyze skill-report-card logs'}]},'response_item'),row({'type':'task_started','turn_id':'second'}),copy.deepcopy(fixture()[3]),copy.deepcopy(fixture()[4]),row({'type':'task_complete'})];r[-3]['payload']['call_id']='other';r[-2]['payload']['call_id']='other';n=parse(encoded(r));self.assertEqual([t['category'] for t in n['turns']],['candidate-real-use','reporting-or-study'])
    def test_browser_hint_does_not_become_metric(self):
        r=fixture();r[3]['payload']['input']+='; page.locator("button").click(); assert.equal(true,true)';t=parse(encoded(r))['turns'][0];self.assertEqual(t['browserActionHintCalls'],1);self.assertEqual(t['assertionHintCalls'],1);self.assertEqual(t['qualityAcceptance'],'not-established')
if __name__=='__main__':unittest.main(verbosity=2)
