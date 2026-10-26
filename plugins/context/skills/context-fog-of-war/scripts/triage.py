"""Qualify diagnostic signals using their own returned evidence, never benchmark truth."""
import re

VERSION='1'

def classify(finding,events):
    from diagnostics import unpack
    result=dict(version=VERSION,state='needs-review',reason='The signal is observed; necessity and harm are not established.',evidence=[],nextEvidence='Record whether this operation was required for the task and whether its outcome blocked acceptance.')
    detector=finding['detector']
    if detector=='repeated-retrieval':
        result['nextEvidence']='Record the purpose of the later read (verification or new information), linked to that call.'
    elif detector in ('retrieved-not-submitted','tool-result-not-propagated'):
        result['nextEvidence']='Record the inclusion requirement or intentional exclusion reason for this item in the target request.'
    elif detector=='truncation':
        result['nextEvidence']='Identify the omitted section and whether the required answer or acceptance evidence was returned.'
        # Only the returned event which owns the truncation signal may qualify it.
        anchor=max(c['traceLine'] for c in finding['evidence'])
        returned=[events[c['eventId']] for c in finding['evidence'] if c['traceLine']==anchor and c['eventId'] in events and events[c['eventId']]['kind']=='result']
        for event in returned:
            if len(event.get('toolCalls',[]))>1:continue  # Sibling output cannot qualify another slot.
            text=unpack(event['evidence']['text'])
            # Require both explicit completion and optional omission, in one assertion.
            benign=re.search(r'(?im)^required (?:answer|evidence) (?:already )?returned; omitted optional [^\n]+$',text)
            conflict=re.search(r'(?im)^(?:required .{0,100}(?:omitted|missing|not returned)|(?:error|failed|failure)\b)',text[:benign.start()]+text[benign.end():] if benign else text)
            if benign and not conflict:
                result.update(state='likely-benign',reason='The returned output reports that required information arrived and only optional material was omitted. This is a reported qualification, not independently verified acceptance.',evidence=[dict(eventId=event['id'],traceLine=anchor,excerpt=event['evidence']['text'])],nextEvidence='Confirm the reported required information satisfies acceptance before treating this as resolved.')
    return result
