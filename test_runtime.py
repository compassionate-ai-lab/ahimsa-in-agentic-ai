"""Acceptance checks for the educational boundary model."""
import unittest
from copy import deepcopy
from dataclasses import replace
from safety_runtime import *

class IndividualBoundary(unittest.TestCase):
    def setUp(self):
        self.g=Gateway();self.p=action();self.c=Context();self.r=safe_risk()

    def test_valid_checked_vector(self):
        result,checked=self.g.evaluate(self.p,self.r,self.c)
        self.assertEqual(result,"permit")
        self.assertAlmostEqual(checked["rights"],.06)

    def test_reject_each_single_dimension_breach(self):
        for k in DIMENSIONS:
            r=deepcopy(self.r);r["estimate"][k]=.5
            self.assertEqual(self.g.evaluate(self.p,r,self.c)[0],"reformulate")

    def test_invalid_numeric_evidence(self):
        for x in [float("nan"),float("inf"),-.01,"0.01",True]:
            r=deepcopy(self.r);r["estimate"]["rights"]=x
            self.assertEqual(self.g.evaluate(self.p,r,self.c)[0],"escalate")

    def test_missing_or_extra_dimension(self):
        for field in ["estimate","margin"]:
            r=deepcopy(self.r);del r[field]["rights"]
            self.assertEqual(self.g.evaluate(self.p,r,self.c)[0],"escalate")
        r=deepcopy(self.r);r["estimate"]["unknown"]=0
        self.assertEqual(self.g.evaluate(self.p,r,self.c)[0],"escalate")

    def test_missing_permission_or_consent(self):
        for c in [replace(self.c,permission=False),replace(self.c,consent=False)]:
            self.assertEqual(self.g.evaluate(self.p,self.r,c)[0],"deny")

    def test_tool_or_actor_outside_scope(self):
        for p in [action(tool="publish"),action(actor="planner")]:
            self.assertEqual(self.g.evaluate(p,self.r,self.c)[0],"deny")

    def test_stale_evidence(self):
        for c in [replace(self.c,evidence_version=6),replace(self.c,evidence_age=1801),replace(self.c,evidence_age=float('nan'))]:
            self.assertEqual(self.g.evaluate(self.p,self.r,c)[0],"refresh")

    def test_action_arguments_changed_after_approval(self):
        _,token=self.g.authorize(self.p,self.r,self.c)
        self.p["args"]["slot"]="S2"
        self.assertEqual(self.g.commit(self.p,token,self.c)[1],"approval-binding")
        self.assertEqual(len(self.g.results),0)

    def test_unknown_approval(self):
        self.assertEqual(self.g.commit(self.p,"forged",self.c)[0],"deny")

    def test_expiry_boundary(self):
        _,token=self.g.authorize(self.p,self.r,self.c,now=100,ttl=60)
        self.assertEqual(self.g.commit(self.p,token,self.c,now=160)[1],"approval-expired")

    def test_state_changed_after_approval(self):
        _,token=self.g.authorize(self.p,self.r,self.c)
        c=replace(self.c,current_version=8,evidence_version=8)
        self.assertEqual(self.g.commit(self.p,token,c)[1],"state")

    def test_consent_revoked_after_approval(self):
        _,token=self.g.authorize(self.p,self.r,self.c)
        self.assertEqual(self.g.commit(self.p,token,replace(self.c,consent=False))[1],"consent")

    def test_policy_changed_after_approval(self):
        _,token=self.g.authorize(self.p,self.r,self.c)
        self.g.policy_version="policy-2"
        self.assertEqual(self.g.commit(self.p,token,replace(self.c,policy_version="policy-2"))[1],"policy")

    def test_identical_retry_does_not_repeat_effect(self):
        _,token=self.g.authorize(self.p,self.r,self.c)
        first=self.g.commit(self.p,token,self.c)
        second=self.g.commit(self.p,token,self.c)
        self.assertEqual(first[0],"committed");self.assertEqual(second[0],"existing")
        self.assertEqual(first[1],second[1])
        self.assertEqual(sum(e["type"]=="simulated-send" for e in self.g.events),1)

    def test_idempotency_key_conflict(self):
        _,token=self.g.authorize(self.p,self.r,self.c);self.g.commit(self.p,token,self.c)
        changed=action(args={"patient":"P2","slot":"S1","template":"slot_available"})
        self.assertEqual(self.g.commit(changed,token,self.c)[1],"key-conflict")

class JointBoundary(unittest.TestCase):
    def setUp(self):self.q=Coordinator()
    def runq(self,key="K1",resources=None,version=7,checks=None,harm=.30,**kw):
        resources=["P1/S1"] if resources is None else resources
        checks=[True]*len(resources) if checks is None else checks
        return self.q.commit_joint(key,resources,version,checks,harm,**kw)
    def test_commit_version_and_retry(self):
        self.assertEqual(self.runq(),"committed");self.assertEqual(self.q.version,8)
        self.assertEqual(self.runq(),"existing");self.assertEqual(self.q.version,8)
    def test_collective_breach_does_not_commit(self):
        self.assertEqual(self.runq(harm=.55),"deny-collective")
        self.assertEqual(self.q.reservations,{})
    def test_individual_breach(self):
        self.assertEqual(self.runq(checks=[False]),"deny-individual")
    def test_capacity_failure_is_atomic(self):
        self.assertEqual(self.runq(resources=["P1/S1","P2/S2","P3/S3"]),"deny-capacity")
        self.assertEqual(self.q.reservations,{})
    def test_duplicate_in_batch(self):
        self.assertEqual(self.runq(resources=["P1/S1","P1/S1"]),"deny-duplicate")
    def test_already_reserved(self):
        self.runq();self.assertEqual(self.runq(key="K2",version=8),"deny-duplicate")
    def test_different_patient_same_physical_slot(self):
        self.runq();self.assertEqual(self.runq(key="K2",resources=["P2/S1"],version=8),"deny-duplicate")
    def test_shared_physical_slot_within_batch(self):
        self.assertEqual(self.runq(resources=["P1/S1","P2/S1"]),"deny-duplicate")
    def test_changed_key_intent(self):
        self.runq();self.assertEqual(self.runq(resources=["P2/S2"]),"deny-key-conflict")
    def test_stale_state(self):
        self.runq();self.assertEqual(self.runq(key="K2",resources=["P2/S2"]),"refresh-state")
    def test_unknown_collective_risk(self):
        self.assertEqual(self.runq(harm=float('nan')),"deny-collective")
    def test_absent_consent_or_authority(self):
        self.assertEqual(self.runq(consent=False),"deny-consent")
        self.assertEqual(self.runq(permission=False),"deny-authority")

class InputBoundary(unittest.TestCase):
    def test_empty_or_invalid_limit_registry_cannot_pass(self):
        self.assertFalse(within_limits({}, {}))
        for cap in [float("nan"), float("inf"), -.1, True]:
            self.assertFalse(within_limits({"rights": 0}, {"rights": cap}))

    def test_malformed_commit_cannot_execute(self):
        g=Gateway();c=Context()
        for proposal in [None, [], "send", {"actor":"reminder-agent", "key":[]}]:
            self.assertEqual(g.commit(proposal,"unknown",c)[0], "deny")
        _,token=g.authorize(action(),safe_risk(),c)
        self.assertEqual(g.commit(action(),[],c)[0],"deny")
        self.assertEqual(g.results,{})

    def test_permission_requires_explicit_true(self):
        for permission in ["yes", 1, None, []]:
            g=Gateway();c=replace(Context(), permission=permission)
            self.assertEqual(g.authorize(action(),safe_risk(),c)[0],"deny")
            q=Coordinator()
            self.assertEqual(q.commit_joint("K1",["P1/S1"],7,[True],.3,
                                           permission=permission),"deny-authority")

    def test_malformed_resource_cannot_consume_capacity(self):
        for resource in [None, "P1/S1", [], ["/S1"], ["P1/"], ["P1/S1/X"]]:
            q=Coordinator()
            self.assertEqual(q.commit_joint("K1",resource,7,[True],.3),"deny-resources")
            self.assertEqual(q.reservations,{})
            self.assertEqual(q.version,7)

    def test_invalid_local_checks_do_not_commit(self):
        q=Coordinator()
        self.assertEqual(q.commit_joint("K1",["P1/S1"],7,None,.3),"deny-individual")
        self.assertEqual(q.reservations,{})

    def test_competing_threads_cannot_reserve_same_slot(self):
        from concurrent.futures import ThreadPoolExecutor
        q=Coordinator()
        def attempt(i):
            return q.commit_joint("K"+str(i),["P"+str(i)+"/S1"],7,[True],.3)
        with ThreadPoolExecutor(max_workers=8) as pool:
            results=list(pool.map(attempt,range(20)))
        self.assertEqual(results.count("committed"),1)
        self.assertEqual(len(q.reservations),1)
        self.assertEqual(q.version,8)

class CoordinatorConfiguration(unittest.TestCase):
    def test_invalid_configuration_is_rejected(self):
        nan, inf = float("nan"), float("inf")
        for kw in ({"ceiling": nan}, {"ceiling": inf}, {"ceiling": -0.1}, {"ceiling": "0.4"},
                   {"capacity": nan}, {"capacity": 0}, {"capacity": 2.0}, {"capacity": True},
                   {"version": -1}, {"version": 7.0}):
            with self.assertRaises(ValueError, msg=str(kw)):
                Coordinator(**kw)

    def test_valid_configuration_still_enforces_ceiling(self):
        q = Coordinator(ceiling=0.4)
        self.assertEqual(q.commit_joint("K", ["P1/S1"], 7, [True], 0.55), "deny-collective")


class RecordIntegrity(unittest.TestCase):
    def setUp(self):
        self.events=[{"type":t} for t in ["propose","check","block","reformulate","recheck"]]
        self.rows=chain(self.events)
    def test_full_sha256_and_valid_chain(self):
        self.assertTrue(all(len(x['digest'])==64 for x in self.rows))
        self.assertEqual(verify_chain(self.rows),(True,None))
    def test_edited_third_event_localizes_mismatch(self):
        self.rows[2]["record"]["event"]["type"]="approve"
        self.assertEqual(verify_chain(self.rows),(False,3))
    def test_deletion_or_reordering(self):
        for rows in [self.rows[:1]+self.rows[2:],list(reversed(self.rows))]:
            self.assertFalse(verify_chain(rows)[0])
    def test_whole_chain_rewrite_needs_external_anchor(self):
        checkpoint=self.rows[-1]['digest']
        self.events[2]["type"]="approve";rewritten=chain(self.events)
        self.assertTrue(verify_chain(rewritten)[0])
        self.assertFalse(verify_chain(rewritten,checkpoint)[0])

if __name__=="__main__":unittest.main()
