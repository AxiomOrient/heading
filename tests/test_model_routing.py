"""Deterministic routing/adapter contracts; these are not model-quality benchmarks."""
from __future__ import annotations

from copy import deepcopy
import importlib.util
import itertools
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / 'plugins/heading/skills/heading-orchestrate'


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'cannot load {path}')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ROUTER = load('heading_routing_tests', BASE / 'scripts/model_routing.py')
RUNNER = load('heading_eval_tests', ROOT / 'scripts/run-evals.py')
POLICY = ROUTER.load_policy()
EASY = {'clarity': 'clear', 'scope': 'local', 'reversible': True, 'oracle': 'strong', 'risk': 'routine'}


class ModelRoutingTests(unittest.TestCase):
    def test_pinned_routing_vectors(self):
        corpus = json.loads((ROOT / 'evals/model-routing-cases.json').read_text())
        self.assertEqual(len(corpus['cases']), 33)
        for case in corpus['cases']:
            with self.subTest(case=case['id']):
                actual = ROUTER.select(case['input'], POLICY)
                for key, value in case['expected'].items():
                    self.assertEqual(actual[key], value)
                self.assertIsNone(actual['effectiveModel'])
                self.assertIsNone(actual['effectiveReasoningEffort'])
                self.assertEqual(actual['modelEscalation'], 'NOT_PROVEN')

    def test_exhaustive_task_classification(self):
        # All 216 combinations: easy requires every positive fact; critical is risk-first.
        facts = list(POLICY['facts']) + ['reversible']
        options = [POLICY['facts'][key] for key in facts[:-1]] + [[True, False, None]]
        count = 0
        for values in itertools.product(*options):
            task = dict(zip(facts, values))
            result = ROUTER.select({'task': task}, POLICY)
            critical = task['risk'] == 'critical' or task['risk'] == 'material' and task['reversible'] is False
            expected = 'astra-high' if critical else 'luna-xhigh' if task == EASY else 'astra-low'
            self.assertEqual(result['routeKey'], expected, task)
            count += 1
        self.assertEqual(count, 216)

    def test_transition_is_pure_and_repeatable(self):
        payload = {'task': deepcopy(EASY)}
        before = deepcopy(payload), deepcopy(POLICY)
        self.assertEqual(ROUTER.select(payload, POLICY), ROUTER.select(payload, POLICY))
        self.assertEqual((payload, POLICY), before)

    def test_missing_unknown_and_wrongly_typed_facts_fail(self):
        invalid = [None, [], {}, {'task': {}}, {'task': EASY, 'model': 'gpt-6-astra'}]
        for key in EASY:
            task = deepcopy(EASY); task.pop(key)
            invalid.append({'task': task})
        for key, value in [('reversible', 1), ('reversible', 'true'), ('risk', []), ('scope', 'small')]:
            task = deepcopy(EASY); task[key] = value
            invalid.append({'task': task})
        for option in ('allowMax', 'boundedSearch'):
            invalid.append({'task': EASY, option: 1})
        for payload in invalid:
            with self.subTest(payload=payload), self.assertRaises(ROUTER.RoutingError):
                ROUTER.select(payload, POLICY)

    def test_history_requires_observed_failure_reference(self):
        invalid = [None, {}, [None], [{}], [{'route':'luna-xhigh','failure':'reasoning','evidence':''}],
                   [{'route':'unknown','failure':'reasoning','evidence':'log:1'}],
                   [{'route':'luna-xhigh','failure':'success','evidence':'log:1'}]]
        for history in invalid:
            with self.subTest(history=history), self.assertRaises(ROUTER.RoutingError):
                ROUTER.select({'task': EASY, 'history': history}, POLICY)

    def test_retry_limit_cannot_be_evaded_by_repeating_failure(self):
        entry = {'route':'luna-xhigh','failure':'reasoning','evidence':'tests/log:1'}
        with self.assertRaises(ROUTER.RoutingError):
            ROUTER.select({'task': EASY, 'history': [entry, entry]}, POLICY)

    def test_effort_and_model_ids_are_not_ui_aliases(self):
        for model, effort in [('gpt-6-astra','none'),('gpt-6-astra','light'),('astra-low','low'),
                              ('gpt-6-astra-pro','low'),('gpt-5.6-luna','ultra')]:
            with self.subTest(model=model, effort=effort), self.assertRaises(ROUTER.RoutingError):
                ROUTER.validate_pair(model, effort, POLICY)
        for model, efforts in POLICY['models'].items():
            for effort in efforts:
                ROUTER.validate_pair(model, effort, POLICY)

    def test_observed_fields_must_match_model_and_locked_authority(self):
        request = ROUTER.select({'task': EASY}, POLICY)
        expected = {'taskId':'child-1','role':'heading_executor','sandbox':'workspace-write'}
        observation = {**expected,'source':'host-metadata','model':request['requestedModel'],
                       'effort':request['requestedReasoningEffort'],'evidenceRef':'host/session.json:1'}
        self.assertEqual(ROUTER.observation_status(request, observation, expected=expected), 'MATCHED_HOST_FIELDS')
        for key in observation:
            bad = deepcopy(observation); bad[key] = '' if key == 'evidenceRef' else 'wrong'
            self.assertEqual(ROUTER.observation_status(request,bad,expected=expected), 'NOT_PROVEN', key)
        self.assertEqual(ROUTER.observation_status(request,observation,expected={}), 'NOT_PROVEN')
        bad = dict(request, routingStatus='REPAIR_REQUIRED')
        self.assertEqual(ROUTER.observation_status(bad,observation,expected=expected), 'NOT_PROVEN')
        self.assertIsNone(request['effectiveModel'])

    def test_role_files_cannot_override_task_route(self):
        for path in (ROOT/'runtime/heading/agents').glob('*.toml'):
            role = tomllib.loads(path.read_text())
            self.assertNotIn('model', role)
            self.assertNotIn('model_reasoning_effort', role)
            self.assertEqual(role['sandbox_mode'], 'workspace-write' if role['name']=='heading_executor' else 'read-only')

    def test_profile_matches_single_policy_lead_default(self):
        profile = tomllib.loads((ROOT/'runtime/heading/profile/heading.config.toml').read_text())
        route = POLICY['routes'][POLICY['defaults']['lead']]
        self.assertEqual((profile['model'], profile['model_reasoning_effort']), (route['model'],route['effort']))

    def test_policy_or_role_drift_is_rejected(self):
        paths = [('plugins/heading/skills/heading-orchestrate/references/model-policy.json',
                  lambda text: text.replace('"easy": "luna-xhigh"','"easy": "astra-max"')),
                 ('runtime/heading/agents/heading-executor.toml',
                  lambda text: 'model = "gpt-5.6-luna"\n' + text)]
        for relative, mutate in paths:
            with self.subTest(path=relative), tempfile.TemporaryDirectory() as temporary:
                copy = Path(temporary)/'source'
                shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns('.git','__pycache__','eval-results'))
                path = copy/relative;path.write_text(mutate(path.read_text()))
                result = subprocess.run([sys.executable,'-B',str(copy/'scripts/validate.py')],capture_output=True,text=True)
                self.assertNotEqual(result.returncode,0)
                self.assertTrue('digest mismatch' in result.stderr or 'agent fields mismatch' in result.stderr, result.stderr)

    def test_real_helper_cli_and_error_exit(self):
        command = [sys.executable,'-B',str(BASE/'scripts/model_routing.py')]
        result = subprocess.run(command,input=json.dumps({'task':EASY}),text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout)['routeKey'],'luna-xhigh')
        for raw in ('{','null','{"task":{}}'):
            result = subprocess.run(command,input=raw,text=True,capture_output=True)
            self.assertEqual(result.returncode,2)
            self.assertEqual(result.stdout,'')
            self.assertIn('model-routing:',result.stderr)

    def test_native_eval_command_sets_model_and_effort_together(self):
        for route in POLICY['routes'].values():
            command = RUNNER.command_for('codex',Path('/repo'),Path('/result'),'prompt',route)
            self.assertEqual(command[command.index('--model')+1],route['model'])
            self.assertEqual(command[command.index('-c')+1],f'model_reasoning_effort="{route["effort"]}"')
            self.assertEqual(command[command.index('--sandbox')+1],'read-only')
        self.assertNotIn('--model',RUNNER.command_for('codex',Path('/repo'),Path('/result'),'prompt'))

    def test_native_eval_route_dry_run_is_not_execution(self):
        result = subprocess.run([sys.executable,'-B',str(ROOT/'scripts/run-evals.py'),
                                 '--dry-run','--limit','1','--route','astra-low'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        payload=json.loads(result.stdout)
        self.assertEqual(payload['status'],'DRY_RUN')
        self.assertIn('gpt-6-astra',payload['plan'][0]['command'])

    def test_timeout_keeps_bytes_evidence_and_never_claims_success(self):
        # A unit test of the failure adapter only; no claim about Codex production behavior.
        error = subprocess.TimeoutExpired(['codex'],1,output=b'{"event":"partial"}\n',stderr=b'partial error')
        with patch.object(RUNNER.subprocess,'run',side_effect=error):
            stdout,stderr,meta = RUNNER.execute_case(['codex'],ROOT,{},1)
        self.assertIn('partial',stdout)
        self.assertIn('TIMEOUT',stderr)
        self.assertIsNone(meta['exitCode'])
        self.assertEqual(meta['executionStatus'],'TIMEOUT')
        self.assertGreaterEqual(meta['durationSeconds'],0)

    def test_missing_executable_returns_observed_spawn_failure(self):
        stdout,stderr,meta=RUNNER.execute_case(['/nonexistent/heading-codex'],ROOT,dict(os.environ),1)
        self.assertEqual(stdout,'')
        self.assertTrue(stderr)
        self.assertEqual(meta['executionStatus'],'SPAWN_FAILED')
        self.assertIsNone(meta['exitCode'])

    def test_actual_subprocess_exit_is_preserved(self):
        stdout,stderr,meta=RUNNER.execute_case([sys.executable,'-c','print("observed");raise SystemExit(7)'],ROOT,dict(os.environ),2)
        self.assertEqual(stdout.strip(),'observed')
        self.assertEqual(meta['exitCode'],7)
        self.assertEqual(meta['executionStatus'],'EXITED')

        stdout,stderr,meta=RUNNER.execute_case(
            [sys.executable,'-c','import time;print("partial",flush=True);time.sleep(2)'],
            ROOT,dict(os.environ),1)
        self.assertIn('partial',stdout)
        self.assertIn('TIMEOUT',stderr)
        self.assertEqual(meta['executionStatus'],'TIMEOUT')
        self.assertIsNone(meta['exitCode'])


    def test_invalid_eval_timeout_fails_before_execution(self):
        result=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/run-evals.py'),'--timeout','0','--dry-run'],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertIn('positive',result.stderr)
