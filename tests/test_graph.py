"""Integration tests run real FalkorDB, including the action boundary."""
import secrets
import pytest
from fastapi.testclient import TestClient

from app import app
from backend import actions
from backend.database import graph_for, rows
from backend.tools import compare_depth, investigate


@pytest.fixture
def workspace():
    key = secrets.token_hex(16)
    return key, graph_for(key)


def test_multihop_scope_repack_rework_and_no_double_count(workspace):
    _, graph = workspace
    scope = compare_depth(graph, 'LOT-SM-2407')
    assert scope['comparison']['one_hop']['units'] == 0
    assert scope['totals']['units'] == 1180
    assert scope['totals']['shipments'] == 6
    assert scope['totals']['review_units'] == 300
    assert {s['id'] for s in scope['confirmed']} == {'SH-101','SH-102','SH-103','SH-104','SH-105','SH-106'}
    assert next(s for s in scope['confirmed'] if s['id']=='SH-106')['path'] == ['LOT-SM-2407','MIX-091','LOT-CR-118','LOT-RW-121']
    assert 'SH-108' not in {s['id'] for s in scope['confirmed'] + scope['uncertain']}


def test_unknown_and_injection_produce_no_invented_scope(workspace):
    _, graph = workspace
    for value in ['LOT-NOT-REAL', "x'}) MATCH (n) DETACH DELETE n //"]:
        result = investigate(graph, value)
        assert result['outcome'] == 'unknown_lot'
        assert result['confirmed'] == []
    assert investigate(graph,'LOT-SM-2407')['totals']['units'] == 1180
    with pytest.raises(ValueError):
        investigate(graph,'LOT-SM-2407',99)


def test_review_action_is_exact_idempotent_and_excludes_ambiguity(workspace):
    key, graph = workspace
    plan = actions.prepare(graph,key,'LOT-SM-2407')
    assert plan['units'] == 1180
    decision = actions.commit(graph,key,plan['token'],True)
    assert not decision['replayed']
    assert actions.commit(graph,key,plan['token'],True)['replayed']
    statuses = rows(graph,"MATCH (s:Shipment) WHERE s.id IN $ids RETURN s.id AS id,s.status AS status",{'ids':['SH-101','SH-107','SH-108']})
    assert {r['id']:r['status'] for r in statuses} == {'SH-101':'held','SH-107':'delivered','SH-108':'warehouse'}


def test_cross_workspace_tampered_expired_and_stale_plans_rejected(workspace):
    key,graph=workspace
    plan=actions.prepare(graph,key,'LOT-SM-2407',now=100)
    with pytest.raises(actions.ActionError,match='different workspace'):
        actions.commit(graph,secrets.token_hex(16),plan['token'],True,now=101)
    with pytest.raises(actions.ActionError,match='invalid'):
        actions.commit(graph,key,plan['token']+'x',True,now=101)
    with pytest.raises(actions.ActionError,match='expired'):
        actions.commit(graph,key,plan['token'],True,now=1000)
    fresh=actions.prepare(graph,key,'LOT-SM-2407')
    graph.query("MATCH (m:Meta) SET m.revision=m.revision+1")
    with pytest.raises(actions.ActionError,match='changed'):
        actions.commit(graph,key,fresh['token'],True)
    after_reset=actions.prepare(graph,key,'LOT-SM-2407')
    graph.query("MATCH (m:Meta) SET m.epoch=$epoch",{'epoch':secrets.token_hex(16)})
    with pytest.raises(actions.ActionError,match='changed'):
        actions.commit(graph,key,after_reset['token'],True)


def test_api_csrf_origin_validation_and_separate_sessions():
    a,b=TestClient(app),TestClient(app)
    wa=a.get('/api/workspace'); wb=b.get('/api/workspace')
    assert wa.status_code == wb.status_code == 200
    token=wa.json()['csrf']; headers={'x-lotline-csrf':token}
    assert a.post('/api/plan',json={'lot_id':'LOT-SM-2407'}).status_code == 403
    assert a.post('/api/plan',json={'lot_id':'LOT-SM-2407'},headers={**headers,'origin':'https://evil.invalid'}).status_code == 403
    assert a.post('/api/investigate',json={'question':'trace','lot_id':'LOT-SM-2407','depth':100},headers=headers).status_code == 422
    plan=a.post('/api/plan',json={'lot_id':'LOT-SM-2407'},headers=headers).json()
    assert b.post('/api/commit',json={'token':plan['token'],'approved':True},headers={'x-lotline-csrf':wb.json()['csrf']}).status_code == 403
    assert a.post('/api/commit',json={'token':plan['token'],'approved':True},headers=headers).status_code == 200
    assert b.get('/api/history').json()['decisions'] == []
