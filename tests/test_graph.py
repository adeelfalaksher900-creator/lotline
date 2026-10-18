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
    graph = graph_for(key)
    try:
        yield key, graph
    finally:
        from backend.database import LOCK, _initialized
        with LOCK:
            graph.delete()
            _initialized.pop(f'lotline_{key}', None)


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


@pytest.mark.parametrize('relationship', ['DISPATCHED', 'DELIVERED_TO'])
def test_unverified_dispatch_or_delivery_cannot_enter_hold(workspace, relationship):
    key, graph = workspace
    if relationship == 'DISPATCHED':
        graph.query("MATCH ()-[r:DISPATCHED]->(s:Shipment {id:'SH-101'}) SET r.evidence='unverified'")
    else:
        graph.query("MATCH (s:Shipment {id:'SH-101'})-[r:DELIVERED_TO]->() SET r.evidence='unverified'")
    scope = investigate(graph, 'LOT-SM-2407')
    assert scope['totals']['units'] == 940
    assert scope['totals']['review_units'] == 540
    assert 'SH-101' not in {s['id'] for s in actions.prepare(graph, key, 'LOT-SM-2407')['shipments']}


def test_session_and_review_tokens_have_separate_purposes(workspace):
    key, graph = workspace
    plan = actions.prepare(graph, key, 'LOT-SM-2407')
    with pytest.raises(actions.ActionError, match='invalid'):
        actions.verify(plan['token'], 'session')
    session = actions.sign({'workspace': key, 'expires': 9999999999}, 'session')
    with pytest.raises(actions.ActionError, match='invalid'):
        actions.commit(graph, key, session, True)


def test_request_body_limit_includes_chunked_input_and_origin_scheme():
    client = TestClient(app)
    headers = {'x-lotline-csrf': client.get('/api/workspace').json()['csrf']}
    assert client.post('/api/plan', json={'lot_id':'LOT-SM-2407'}, headers={**headers, 'origin':'https://testserver'}).status_code == 403
    assert client.post('/api/plan', json={'lot_id':'LOT-SM-2407'}, headers={**headers, 'origin':'http://['}).status_code == 403
    for content in [b'x' * 8001, iter([b'x' * 4000, b'x' * 4001])]:
        assert client.post('/api/plan', content=content, headers={**headers, 'content-type':'application/json'}).status_code == 413


def test_requested_lot_cannot_be_replaced_by_model(monkeypatch):
    from backend import agent
    monkeypatch.setenv('LOTLINE_PLANNER_URL', 'https://planner.invalid/plan')
    class Response:
        def raise_for_status(self): pass
        def json(self): return {'tool':'investigate', 'lot_id':'LOT-MK-311'}
    class Client:
        def __init__(self, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def post(self, *args, **kwargs): return Response()
    monkeypatch.setattr(agent.httpx, 'Client', Client)
    assert agent.select_tool('Investigate LOT-NOT-REAL', 'LOT-SM-2407')['lot_id'] == 'LOT-NOT-REAL'
    assert agent.select_tool('Investigate MIX-091', 'LOT-SM-2407')['lot_id'] == 'MIX-091'
    assert agent.select_tool('Trace this case', 'LOT-SM-2407')['lot_id'] == 'LOT-SM-2407'


def test_embedded_workspaces_expire_and_reject_capacity_without_eviction(monkeypatch):
    from collections import OrderedDict
    from backend import database
    monkeypatch.delenv('FALKORDB_URL', raising=False)
    monkeypatch.setattr(database, '_initialized', OrderedDict())
    monkeypatch.setattr(database, 'MAX_EMBEDDED_WORKSPACES', 1)
    first, second = secrets.token_hex(16), secrets.token_hex(16)
    graph = graph_for(first)
    try:
        assert 0 < database.connection().connection.ttl(f'lotline_{first}') <= 3600
        with pytest.raises(RuntimeError, match='capacity'):
            graph_for(second)
        assert investigate(graph_for(first), 'LOT-SM-2407')['totals']['units'] == 1180
    finally:
        graph.delete()


def test_deployed_favicon_is_served_from_build_output(tmp_path, monkeypatch):
    import app as module
    monkeypatch.setattr(module, 'DIST', tmp_path)
    (tmp_path / 'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
    response = TestClient(app).get('/favicon.svg')
    assert response.status_code == 200
    assert response.headers['content-type'].startswith('image/svg+xml')


def test_partial_scope_never_offers_a_hold(workspace):
    key, graph = workspace
    graph.query("""MATCH (root:Lot {id:'LOT-SM-2407'})
UNWIND range(1,501) AS i
CREATE (lot:Lot {id:'FANOUT-'+toString(i),name:'Synthetic branch',kind:'Lot'})
CREATE (root)-[:INPUT_TO {evidence:'confirmed',source_id:'DOC-02'}]->(lot)""")
    scope = investigate(graph, 'LOT-SM-2407')
    assert scope['outcome'] == 'scope_incomplete'
    assert scope['truncated'] is True
    assert 'totals are partial' in scope['summary']
    with pytest.raises(actions.ActionError, match='complete'):
        actions.prepare(graph, key, 'LOT-SM-2407')
