import copy
import json
import tempfile
import unittest
from pathlib import Path
from shorts_app.agent_workspace import Workspace,script_check
from shorts_app.store import Conflict

SCRIPT={'title':'복수하세요','shots':[{'id':'hook','beats':[{'en':'Make your own.','ko':'직접 만들어 보세요.'}]}]}
DESIGN='export default function Visual(){return null}; export function Cover(){return null}'
class WorkspaceTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.w=Workspace(self.temp.name);self.addCleanup(self.w.pool.shutdown)
  self.p=self.w.create('에이전트가 쇼츠를 제작한다')
 def test_create_does_not_call_a_model_or_start_a_job(self):
  self.assertIsNone(self.p['script']);self.assertEqual(self.p['job'],{})
 def test_freeform_script_needs_no_diagram_or_values(self):
  script_check(SCRIPT)
  p=self.w.script_write(self.p['id'],0,SCRIPT)
  self.assertEqual(p['script'],SCRIPT)
 def test_design_revision_preserves_speech_but_invalidates_render(self):
  p=self.w.script_write(self.p['id'],0,SCRIPT);p['speech']=[{'actual':'cue'}];p['delivery']={'old':'render'};self.w.put(p)
  p=self.w.design_write(p['id'],1,DESIGN)
  self.assertEqual(p['speech'],[{'actual':'cue'}]);self.assertIsNone(p['delivery'])
  original=self.w.folder(p['id'])/p['design']
  p=self.w.design_write(p['id'],2,DESIGN+'\n// revised')
  self.assertEqual(original.read_text(),DESIGN)
 def test_conflicts_and_running_stage_block_edits(self):
  self.w.script_write(self.p['id'],0,SCRIPT)
  with self.assertRaises(Conflict):self.w.design_write(self.p['id'],0,DESIGN)
  p=self.w.read(self.p['id']);p['job']={'status':'running'};self.w.put(p)
  with self.assertRaises(Conflict):self.w.design_write(p['id'],1,DESIGN)
 def test_script_edit_invalidates_returned_cues(self):
  p=self.w.script_write(self.p['id'],0,SCRIPT);p['speech']=[{'old':'cue'}];self.w.put(p)
  new=copy.deepcopy(SCRIPT);new['shots'][0]['beats'][0]['ko']='당신도 만들어 보세요.'
  self.assertIsNone(self.w.script_write(p['id'],1,new)['speech'])
 def test_stage_requires_script_speech_design(self):
  with self.assertRaises(ValueError):self.w.start(self.p['id'],'speech')
  self.w.script_write(self.p['id'],0,SCRIPT)
  with self.assertRaises(ValueError):self.w.start(self.p['id'],'render')
 def test_recovery_is_explicit_after_process_lock(self):
  p=self.p;p['job']={'status':'running'};self.w.put(p)
  second=Workspace(self.temp.name);self.addCleanup(second.pool.shutdown)
  self.assertEqual(second.read(p['id'])['job']['status'],'running')
  second.recover();self.assertEqual(second.read(p['id'])['job']['status'],'interrupted')
 def test_image_and_project_paths_are_confined(self):
  with self.assertRaises(ValueError):self.w.read('../other')
  p=self.p;p['preview']={'folder':'renders/abc','frames':['frame-00030.png']};self.w.put(p)
  with self.assertRaises(ValueError):self.w.image_path(p['id'],'../../secret.png')
 def test_final_review_is_bound_to_current_render(self):
  with self.assertRaises(ValueError):self.w.review(self.p['id'],0,'Observed the frames and playback.',True)
  p=self.p;p['delivery']={'folder':'renders/abc'};self.w.put(p)
  result=self.w.review(p['id'],0,'Observed the frames and playback; audio listening pending.',True)
  self.assertEqual(result['review']['render'],'renders/abc')
