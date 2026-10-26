import importlib.util,json,os,subprocess,sys,unittest
from pathlib import Path
from unittest.mock import patch
root=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('runner',root/'run.py');runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
class RuntimeTests(unittest.TestCase):
 def test_missing_path_uses_bounded_runtime(self):
  with patch.dict(os.environ,{'PATH':''},clear=False):
   node,version=runner.resolve();self.assertTrue(Path(node).is_file());self.assertTrue(version.startswith('v'))
 def test_explicit_missing_does_not_silently_fallback(self):
  with patch.dict(os.environ,{'UI_NODE_PATH':'/nonexistent/base-ui-node'}):
   with self.assertRaises(SystemExit):runner.resolve()
 def test_command_through_launcher_without_node_path(self):
  result=subprocess.run([sys.executable,str(root/'run.py'),'generate-token-index.mjs','--group','color'],env={**os.environ,'PATH':''},capture_output=True,text=True);self.assertEqual(result.returncode,0,result.stderr);self.assertIn('nextOffset',result.stdout)
 def test_pages_reconstruct_source_without_loss(self):
  file='references/review/principles.md';parts=[];i=0
  while i is not None:
   result=subprocess.run([sys.executable,str(root/'run.py'),'read',file,'--page',str(i)],capture_output=True,text=True,check=True);p=json.loads(result.stdout);self.assertLessEqual(len(p['content'].encode()),4000);parts.append(p['content']);i=p['nextPage']
  self.assertEqual(''.join(parts),(root.parent/file).read_text())
if __name__=='__main__':unittest.main()
