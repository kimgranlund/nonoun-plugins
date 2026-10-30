"""Coverage describes detector eligibility, never correctness or retained context."""
SPECS={
 'failed-discovery':('matched lookup results','Record the lookup request, its matching result, and explicit success/failure status.','An intentional probe can fail without being a routing mistake.'),
 'repeated-retrieval':('comparable consecutive source-return pairs','Record a second return of the same source with full-return or explicit line-range metadata.','Repeated access is not necessarily waste; unrecorded edits or eviction may justify it.'),
 'truncation':('returned output envelopes','Preserve the returned output envelope, including truncation flags or warnings.','Absence of a marker cannot rule out silent truncation upstream.'),
 'broken-reference':('failed literal targets checked against prior guidance','Record a failed literal target and the earlier returned guidance that referenced it.','An exact path mention is not proof that guidance instructed the lookup.'),
 'late-guidance':('first recorded guidance returns','Record guidance returns and governed edits with their order and source paths.','Directory proximity does not prove applicability; earlier injected guidance may be unrecorded.'),
 'retrieved-not-submitted':('linked retrieval/request pairs','Record the target request ID and its complete included-chunk identity list.','A deliberate relevance filter can omit a chunk without a defect.'),
 'tool-result-not-propagated':('linked tool-result/request pairs','Record the target request ID and its complete tool-result identity list.','Intentional result suppression is not necessarily a propagation defect.'),
 'stop-at-cap':('model requests with outputTokens and maxTokens and no stop reason','Record outputTokens and maxTokens on the model_request, or the provider stop reason.','Usage equal to the cap is indirect evidence; a recorded stop reason settles it.'),
 'evaluation-artifact-mismatch':('linked evaluation/delivery hash pairs','Record an explicit delivery ID and SHA256 for both evaluated and delivered bytes.','A comparison may intentionally evaluate an intermediate artifact.')}

from delivery import SPECS as DELIVERY_SPECS
SPECS.update(DELIVERY_SPECS)

class Coverage:
 def __init__(self):self.items={k:{'eligible':0,'blocked':[],'excluded':[]} for k in SPECS}
 def eligible(self,k):self.items[k]['eligible']+=1
 def gap(self,k,reason,request,event=None):
  entry={'reason':reason,'minimumEvidence':request}
  if event:entry['evidence']={'eventId':event['id'],'traceLine':event['evidence']['traceLine'],'excerpt':event['evidence']['text'][:240]}
  self.items[k]['blocked'].append(entry)
 def exclude(self,k,reason):self.items[k]['excluded'].append(reason)
 def finish(self,rows,data):
  warnings=data.get('coverage',{}).get('warnings',[])
  opaque=[w for w in warnings if 'opaque' in w.lower() and ('record(s)' in w or 'verified emitted prefix' in w)]
  for row in rows:
   k=row['detector'];x=self.items[k];unit,request,limit=SPECS[k]
   groups={}
   for b in x['blocked']:
    g=groups.setdefault(b['reason'],dict(reason=b['reason'],count=0,minimumEvidence=b['minimumEvidence'],evidence=[]));g['count']+=1
    if b.get('evidence'):g['evidence'].append(b['evidence'])
   gaps=list(groups.values());eligible=x['eligible']
   if gaps:status='partial' if eligible else 'insufficient-evidence'
   elif eligible:status='findings-observed' if row['findings'] else 'assessed-no-signal'
   else:status='no-eligible-candidates'
   # These detectors have no native request assembly projection in Codex/Claude reports.
   if k in ('retrieved-not-submitted','tool-result-not-propagated','evaluation-artifact-mismatch','stop-at-cap') and not data.get('bundle'):
    status='unavailable-telemetry';gaps=[dict(reason='Required explicit bundle telemetry is absent from this report',count=None,minimumEvidence=request,evidence=[])]
   excluded={reason:x['excluded'].count(reason) for reason in sorted(set(x['excluded']))}
   row['explanation']={'status':status,'eligible':eligible,'unit':unit,'inspected':row['assessed'],'inspectedMeaning':'Legacy detector scan count; not the number of eligible comparisons or defects.',
     'blockedCandidates':len(x['blocked']),'excluded':excluded,'gaps':gaps,
     'nextEvidence':list(dict.fromkeys(g['minimumEvidence'] for g in gaps)),
     'noCandidateExplanation':None if eligible or gaps else 'No eligible trigger was recorded; this is not proof that no problem occurred.',
     'investigationEvidence':request if not eligible and not gaps else None,
     'blindSpots':[limit]+(['Unsupported wrapper records may hide additional inputs; eligibility is a lower bound.'] if opaque else []),
     'coverageWarningEvidence':opaque,
     'opaqueEvidenceRequest':'For an affected wrapper, emit ordered tool names, arguments, status and results; emit a stored path snapshot only if image attribution depends on it.' if opaque else None}
  return rows
