"""Deterministic educational model of individual and joint execution gates.

No external effects, identity provider, durable transactions, clinical inference,
or distributed-consensus implementation. The caller supplies trusted context.
"""
from dataclasses import dataclass
from hashlib import sha256
from json import dumps
from math import isfinite
from threading import RLock
from copy import deepcopy

DIMENSIONS = ("physical", "psychological", "rights", "integrity")

def canonical(value):
    return dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)

def digest(value):
    return sha256(canonical(value).encode("utf-8")).hexdigest()

def number(x, minimum=0):
    return type(x) in (int, float) and isfinite(x) and x >= minimum

def within_limits(checked, ceilings):
    if not ceilings or set(checked) != set(ceilings):
        return False
    return all(number(v) and number(ceilings[k]) and v <= ceilings[k]
               for k, v in checked.items())

@dataclass(frozen=True)
class Context:
    evidence_version: int = 7
    current_version: int = 7
    evidence_age: float = 120
    consent: bool = True
    permission: bool = True
    policy_version: str = "policy-1"

def action(key="K1", actor="reminder-agent", tool="send_reminder",
           args=None):
    return {"key": key, "actor": actor, "tool": tool,
            "args": deepcopy(args if args is not None else
                             {"patient": "P1", "slot": "S1",
                              "template": "slot_available"})}

def safe_risk():
    return {"estimate": dict(zip(DIMENSIONS, (.01, .02, .02, .01))),
            "margin": dict(zip(DIMENSIONS, (.005, .01, .02, .01))),
            "vulnerability": 1.5}

class Gateway:
    """One-process gateway; the authorization registry models trusted issuance."""
    def __init__(self, ceilings=None):
        self.ceilings = dict(ceilings or zip(DIMENSIONS, (.05, .10, .10, .10)))
        if set(self.ceilings) != set(DIMENSIONS) or not all(
                number(x) for x in self.ceilings.values()):
            raise ValueError("invalid policy ceilings")
        self.policy_version = "policy-1"
        self.max_age = 1800
        self.tokens = {}
        self.results = {}
        self.events = []
        self.lock = RLock()

    def evaluate(self, proposal, risk, context):
        if not isinstance(proposal, dict) or set(proposal) != {
                "key", "actor", "tool", "args"}:
            return "deny", "schema"
        if not all(type(proposal[k]) is str and proposal[k].strip()
                   for k in ("key", "actor", "tool")):
            return "deny", "identity"
        if proposal["actor"] != "reminder-agent" or context.permission is not True:
            return "deny", "authority"
        if proposal["tool"] != "send_reminder":
            return "deny", "tool"
        if not isinstance(proposal["args"], dict) or set(proposal["args"]) != {
                "patient", "slot", "template"}:
            return "deny", "arguments"
        if not all(type(v) is str and v.strip()
                   for v in proposal["args"].values()):
            return "deny", "arguments"
        if proposal["args"]["template"] != "slot_available":
            return "reformulate", "template"
        if context.consent is not True:
            return "deny", "consent"
        if context.policy_version != self.policy_version:
            return "refresh", "policy"
        if (context.evidence_version != context.current_version or
            not number(context.evidence_age) or context.evidence_age > self.max_age):
            return "refresh", "evidence"
        try:
            if set(risk) != {"estimate", "margin", "vulnerability"}:
                return "escalate", "risk-schema"
            if not number(risk["vulnerability"], 1):
                return "escalate", "vulnerability"
            if set(risk["estimate"]) != set(DIMENSIONS) or set(
                    risk["margin"]) != set(DIMENSIONS):
                return "escalate", "risk-dimensions"
            if not all(number(x) for d in ("estimate", "margin")
                       for x in risk[d].values()):
                return "escalate", "nonfinite-or-negative"
            checked = {k: risk["vulnerability"] *
                       (risk["estimate"][k] + risk["margin"][k])
                       for k in DIMENSIONS}
            if not within_limits(checked, self.ceilings):
                return "reformulate", "harm-ceiling"
        except (KeyError, TypeError, AttributeError):
            return "escalate", "risk-schema"
        return "permit", checked

    def authorize(self, proposal, risk, context, now=100, ttl=60):
        with self.lock:
            if not number(now) or not number(ttl) or ttl == 0:
                return "deny", "clock"
            decision, reason = self.evaluate(proposal, risk, context)
            self.events.append({"type": "evaluate", "decision": decision,
                                "key": proposal.get("key") if isinstance(proposal,dict) else None})
            if decision != "permit":
                return decision, reason
            token = digest(["authorization", len(self.tokens), proposal, now])
            self.tokens[token] = {"intent": digest(proposal), "risk": deepcopy(risk),
                                  "state": context.current_version,
                                  "policy": self.policy_version, "expires": now+ttl}
            return "permit", token

    def commit(self, proposal, token, context, now=101):
        with self.lock:
            if not isinstance(proposal, dict):
                return "deny", "schema"
            if context.permission is not True or proposal.get("actor") != "reminder-agent":
                return "deny", "authority"
            try:
                intent = digest(proposal)
            except (TypeError, ValueError):
                return "deny", "intent"
            # Read an existing receipt only for the same authorized intent.
            if type(proposal.get("key")) is not str:
                return "deny", "schema"
            prior = self.results.get(proposal.get("key"))
            if prior:
                return ("existing", prior["receipt"]) if prior["intent"] == intent else ("deny", "key-conflict")
            if type(token) is not str:
                return "deny", "approval-binding"
            grant = self.tokens.get(token)
            if grant is None or grant["intent"] != intent:
                return "deny", "approval-binding"
            if not number(now) or now >= grant["expires"]:
                return "deny", "approval-expired"
            if grant["policy"] != self.policy_version or context.policy_version != self.policy_version:
                return "refresh", "policy"
            if grant["state"] != context.current_version:
                return "refresh", "state"
            decision, reason = self.evaluate(proposal, grant["risk"], context)
            if decision != "permit":
                return decision, reason
            receipt = digest(["simulated-send", proposal])
            self.results[proposal["key"]] = {"intent": intent, "receipt": receipt}
            self.events.append({"type": "simulated-send", "key": proposal["key"],
                                "receipt": receipt})
            return "committed", receipt

class Coordinator:
    """Atomic in-memory reservations for a joint plan, no external effects."""
    def __init__(self, capacity=2, version=7, ceiling=.4):
        # Reject invalid configuration at construction: a NaN ceiling would
        # make every "harm > ceiling" test false, and a NaN capacity would
        # make every capacity test false, silently admitting joint plans.
        if type(capacity) is not int or capacity < 1:
            raise ValueError("capacity must be an integer >= 1")
        if type(version) is not int or version < 0:
            raise ValueError("version must be an integer >= 0")
        if not number(ceiling):
            raise ValueError("ceiling must be a finite number >= 0")
        self.capacity = capacity
        self.version = version
        self.ceiling = ceiling
        self.reservations = {}
        self.receipts = {}
        self.lock = RLock()

    def commit_joint(self, key, resources, expected_version,
                     local_checks, collective_harm, consent=True,
                     permission=True):
        with self.lock:
            if permission is not True:
                return "deny-authority"
            if type(key) is not str or not key.strip():
                return "deny-key"
            if (not isinstance(resources, (list, tuple)) or not resources
                or any(type(x) is not str or not x.strip() for x in resources)):
                return "deny-resources"
            if any(len(x.split("/")) != 2 or
                   any(not part.strip() for part in x.split("/"))
                   for x in resources):
                return "deny-resources"
            intent=digest(list(resources))
            if key in self.receipts:
                return "existing" if self.receipts[key] == intent else "deny-key-conflict"
            if consent is not True:
                return "deny-consent"
            if type(expected_version) is not int or expected_version != self.version:
                return "refresh-state"
            if (not isinstance(local_checks, (list, tuple)) or
                len(local_checks) != len(resources) or
                any(x is not True for x in local_checks)):
                return "deny-individual"
            if not number(collective_harm) or collective_harm > self.ceiling:
                return "deny-collective"
            if len(set(resources)) != len(resources) or any(x in self.reservations for x in resources):
                return "deny-duplicate"
            # A patient/slot pair also consumes the slot itself. Different
            # patients must not reserve the same physical slot under new keys.
            if any(len(x.split("/")) != 2 for x in resources):
                return "deny-resources"
            slots=[x.split("/")[1] for x in resources]
            occupied_slots={x.split("/")[1] for x in self.reservations}
            if len(set(slots)) != len(slots) or occupied_slots.intersection(slots):
                return "deny-duplicate"
            if len(self.reservations) + len(resources) > self.capacity:
                return "deny-capacity"
            for resource in resources:
                self.reservations[resource] = key
            self.receipts[key] = intent
            self.version += 1
            return "committed"

def chain(events):
    rows=[]
    previous="0"*64
    for i,event in enumerate(events,1):
        record={"sequence":i,"previous":previous,"event":deepcopy(event)}
        h=digest(record)
        rows.append({"record":record,"digest":h})
        previous=h
    return rows

def verify_chain(rows, checkpoint=None):
    previous="0"*64
    for i,row in enumerate(rows,1):
        try:
            rec=row["record"]
            if rec["sequence"]!=i or rec["previous"]!=previous or digest(rec)!=row["digest"]:
                return False, i
            previous=row["digest"]
        except (KeyError,TypeError,ValueError):
            return False, i
    if checkpoint is not None and previous!=checkpoint:
        return False, len(rows)+1
    return True, None

if __name__ == "__main__":
    g=Gateway();p=action();c=Context()
    decision,token=g.authorize(p,safe_risk(),c)
    print("Individual gate:",decision)
    print("First execution:",g.commit(p,token,c)[0])
    print("Identical retry:",g.commit(p,token,c)[0])
    q=Coordinator()
    print("Joint reservation:",q.commit_joint("K1",["P1/S1"],7,[True],.30))
    print("Collective breach:",q.commit_joint("K2",["P2/S2"],8,[True],.55))
