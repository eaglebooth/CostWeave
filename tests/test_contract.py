import hashlib
import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "samples/ecfr/2-CFR-200.403-2026-10-08.xml"
ALLOW = "This $100 travel cost is necessary for the award field inspection and is allocable only to that inspection task."
DENY = "This $40 entertainment charge is expressly excluded by the Federal award and was nevertheless charged to it."
REVIEW = "This $25 administrative item was entered by the project team without further supporting facts."


def addr(value): return "0x" + bytes(value).hex()
def ns(c): return c._instance.__class__.compile_allocation.__globals__
def body(): return FIXTURE.read_bytes()


def digest_for(c):
    record = ns(c)["parse_ecfr"](body())
    return hashlib.sha256(ns(c)["canonical"](record).encode()).hexdigest()


def web(vm, payload=None, status=200):
    vm.mock_web(r"^https://www\.ecfr\.gov/api/versioner/v1/full/2026-10-08/title-2\.xml\?part=200&section=200\.403$",
                {"method":"GET","status":status,"body":body() if payload is None else payload})


def lines(include_review=False):
    value=[{"line_id":"travel","amount":100,"description":ALLOW},
           {"line_id":"party","amount":40,"description":DENY}]
    if include_review: value.append({"line_id":"admin","amount":25,"description":REVIEW})
    return value


def decision_rows(include_review=False):
    value=[{"line_id":"travel","verdict":"ALLOWABLE_DECLARATION","criterion":"a","excerpt":ALLOW},
           {"line_id":"party","verdict":"UNALLOWABLE_DECLARATION","criterion":"b","excerpt":DENY}]
    if include_review: value.append({"line_id":"admin","verdict":"REVIEW_REQUIRED","criterion":"none","excerpt":""})
    return value


def llm(vm, include_review=False, independent=None):
    leader=decision_rows(include_review); validator=independent if independent is not None else leader
    vm.mock_llm(r"^Compile CostWeave",json.dumps({"decisions":leader}))
    vm.mock_llm(r"^Independently compile CostWeave",json.dumps({"decisions":validator}))


def setup(direct_deploy, vm, owner, reviewer, consumer, include_review=False, local_id="batch"):
    c=direct_deploy("contracts/cost_weave.py")
    with vm.prank(owner):
        bid=c.create_batch(local_id,addr(reviewer),addr(consumer),"2026-10-08","USD_CENTS",json.dumps(lines(include_review)))
    snap=json.loads(c.get_batch(bid))["snapshot_digest"]
    with vm.prank(reviewer): c.accept_batch(bid,snap)
    return c,bid


def state(c,bid): return json.loads(c.get_batch(bid))


def test_atomic_vector_conservation_and_consumption(direct_deploy,direct_vm,direct_alice,direct_bob):
    c,bid=setup(direct_deploy,direct_vm,direct_alice,direct_bob,direct_bob)
    web(direct_vm); llm(direct_vm)
    assert c.compile_allocation(bid,0,digest_for(c))=="COMPILED"
    row=state(c,bid)
    assert (row["total"],row["allowable_total"],row["unallowable_total"],row["review_total"])==(140,100,40,0)
    assert sum((row["allowable_total"],row["unallowable_total"],row["review_total"]))==row["total"]
    with direct_vm.prank(direct_bob): c.consume_compilation(bid,1)
    assert state(c,bid)["status"]=="CONSUMED"
    before=c.get_batch(bid)
    with direct_vm.prank(direct_bob),direct_vm.expect_revert("COMPILATION_NOT_AVAILABLE"):
        c.consume_compilation(bid,1)
    assert c.get_batch(bid)==before


def test_review_line_blocks_consumption(direct_deploy,direct_vm,direct_alice,direct_bob):
    c,bid=setup(direct_deploy,direct_vm,direct_alice,direct_bob,direct_bob,True)
    web(direct_vm); llm(direct_vm,True)
    assert c.compile_allocation(bid,0,digest_for(c))=="REVIEW_REQUIRED"
    row=state(c,bid); assert (row["total"],row["review_total"])==(165,25)
    before=c.get_batch(bid)
    with direct_vm.prank(direct_bob),direct_vm.expect_revert("COMPILATION_NOT_AVAILABLE"):
        c.consume_compilation(bid,1)
    assert c.get_batch(bid)==before


def test_vector_order_cannot_misallocate_amounts(direct_deploy,direct_vm,direct_alice,direct_bob):
    c,bid=setup(direct_deploy,direct_vm,direct_alice,direct_bob,direct_bob)
    shuffled=list(reversed(decision_rows()))
    web(direct_vm)
    direct_vm.mock_llm(r"^Compile CostWeave",json.dumps({"decisions":shuffled}))
    direct_vm.mock_llm(r"^Independently compile CostWeave",json.dumps({"decisions":shuffled}))
    assert c.compile_allocation(bid,0,digest_for(c))=="COMPILED"
    row=state(c,bid)
    assert row["allowable_total"]==100 and row["unallowable_total"]==40


def test_deployer_no_role_and_reviewer_auth(direct_deploy,direct_vm,direct_alice,direct_bob):
    c=direct_deploy("contracts/cost_weave.py")
    with direct_vm.prank(direct_alice):
        bid=c.create_batch("roles",addr(direct_bob),addr(direct_bob),"2026-10-08","USD_CENTS",json.dumps(lines()))
    before=c.get_batch(bid)
    with direct_vm.expect_revert("REVIEWER_ONLY"):
        c.accept_batch(bid,state(c,bid)["snapshot_digest"])
    assert c.get_batch(bid)==before


def test_wrong_snapshot_and_consumer_rollback(direct_deploy,direct_vm,direct_alice,direct_bob):
    c=direct_deploy("contracts/cost_weave.py")
    with direct_vm.prank(direct_alice): bid=c.create_batch("guards",addr(direct_bob),addr(direct_bob),"2026-10-08","USD_CENTS",json.dumps(lines()))
    before=c.get_batch(bid)
    with direct_vm.prank(direct_bob),direct_vm.expect_revert("SNAPSHOT_MISMATCH"): c.accept_batch(bid,"0"*64)
    assert c.get_batch(bid)==before


def test_wrong_source_digest_rollback(direct_deploy,direct_vm,direct_alice,direct_bob):
    c,bid=setup(direct_deploy,direct_vm,direct_alice,direct_bob,direct_bob)
    web(direct_vm); llm(direct_vm); before=c.get_batch(bid)
    with direct_vm.expect_revert("SOURCE_DIGEST_MISMATCH"): c.compile_allocation(bid,0,"0"*64)
    assert c.get_batch(bid)==before


@pytest.mark.parametrize("status",[301,404,429,500])
def test_source_failure_fails_closed(direct_deploy,direct_vm,direct_alice,direct_bob,status):
    c,bid=setup(direct_deploy,direct_vm,direct_alice,direct_bob,direct_bob)
    web(direct_vm,status=status)
    assert c.compile_allocation(bid,0,digest_for(c))=="REVIEW_REQUIRED"
    row=state(c,bid); assert row["review_total"]==row["total"] and row["source_digest"]==""


@pytest.mark.parametrize("attack",["wrong_section","cross_container","missing_rule","duplicate","oversized","bad_utf8"])
def test_poisoned_source_fails_closed(direct_deploy,direct_vm,direct_alice,direct_bob,attack):
    c,bid=setup(direct_deploy,direct_vm,direct_alice,direct_bob,direct_bob)
    raw=body()
    if attack=="wrong_section": payload=raw.replace(b'200.403',b'200.404')
    elif attack=="cross_container": payload=(b'<?xml version="1.0" encoding="UTF-8"?>'
        b'<DIV8 N="200.403" TYPE="SECTION"></DIV8>'+raw.replace(b'200.403',b'200.404'))
    elif attack=="missing_rule": payload=raw.replace(b'<P>(h)',b'<P>(z)')
    elif attack=="duplicate": payload=raw.replace(b'</DIV8>',b'<P>(a) duplicate criterion text that is long enough.</P></DIV8>')
    elif attack=="oversized": payload=b"<DIV8>"+b" "*16001
    else: payload=b"\xff"
    web(direct_vm,payload)
    assert c.compile_allocation(bid,0,digest_for(c))=="REVIEW_REQUIRED"
    assert state(c,bid)["source_digest"]==""


def test_malformed_model_never_positive(direct_deploy,direct_vm,direct_alice,direct_bob):
    c,bid=setup(direct_deploy,direct_vm,direct_alice,direct_bob,direct_bob)
    web(direct_vm); direct_vm.mock_llm(r"^Compile CostWeave",'{"decisions":[]}')
    assert c.compile_allocation(bid,0,digest_for(c))=="REVIEW_REQUIRED"


def test_same_url_valid_changed_source_digest_rolls_back(direct_deploy,direct_vm,direct_alice,direct_bob):
    c,bid=setup(direct_deploy,direct_vm,direct_alice,direct_bob,direct_bob)
    changed=body().replace(b'Be necessary and reasonable',b'Be demonstrably necessary and reasonable')
    assert ns(c)["parse_ecfr"](changed)
    web(direct_vm,changed); before=c.get_batch(bid)
    with direct_vm.expect_revert("SOURCE_DIGEST_MISMATCH"):
        c.compile_allocation(bid,0,digest_for(c))
    assert c.get_batch(bid)==before


def test_validator_rejects_different_vector(direct_deploy,direct_vm,direct_alice,direct_bob):
    c,bid=setup(direct_deploy,direct_vm,direct_alice,direct_bob,direct_bob)
    changed=decision_rows(); changed[0]={"line_id":"travel","verdict":"REVIEW_REQUIRED","criterion":"none","excerpt":""}
    web(direct_vm); llm(direct_vm,independent=changed)
    c.compile_allocation(bid,0,digest_for(c))
    assert direct_vm.run_validator() is False


def test_validator_accepts_equivalent_vector_order(direct_deploy,direct_vm,direct_alice,direct_bob):
    c,bid=setup(direct_deploy,direct_vm,direct_alice,direct_bob,direct_bob)
    web(direct_vm); llm(direct_vm,independent=list(reversed(decision_rows())))
    c.compile_allocation(bid,0,digest_for(c))
    assert direct_vm.run_validator() is True


def test_stale_replay_and_unauthorized_consumer(direct_deploy,direct_vm,direct_alice,direct_bob):
    c,bid=setup(direct_deploy,direct_vm,direct_alice,direct_bob,direct_bob)
    web(direct_vm); llm(direct_vm); c.compile_allocation(bid,0,digest_for(c)); before=c.get_batch(bid)
    with direct_vm.expect_revert("BATCH_NOT_COMPILABLE"): c.compile_allocation(bid,0,digest_for(c))
    with direct_vm.prank(direct_alice),direct_vm.expect_revert("CONSUMER_ONLY"): c.consume_compilation(bid,1)
    assert c.get_batch(bid)==before


def test_input_bounds_and_parser(direct_deploy,direct_vm,direct_alice,direct_bob):
    c=direct_deploy("contracts/cost_weave.py")
    parser=ns(c)["parse_ecfr"]; record=parser(body())
    assert set(record["criteria"])==set("abcdefgh")
    version=json.loads(c.get_version()); assert version["name"]=="CostWeave" and version["max_lines"]==6
    with direct_vm.prank(direct_alice),direct_vm.expect_revert("INVALID_BATCH"):
        c.create_batch("bad","not-address",addr(direct_bob),"2026-10-08","USD_CENTS",json.dumps(lines()))

