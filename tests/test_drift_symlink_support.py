"""Controlled drift aliases and complete transactional state fingerprints."""
import hashlib

from test_lane_tracer import execute_gate, make_candidate, setup_host
from test_reconcile_lane_support import fixture

from hmt_rnd.host_models import Clock


def replace_with_link(path, root, dangling=False):
    target = root / (path.name + ".replacement")
    if not dangling:
        target.write_bytes(b"changed source behind symlink")
    path.unlink()
    path.symlink_to(target)


def state(host):
    names = ("lane_candidates", "lane_artifacts", "lane_reopens", "lane_invalidations",
             "lane_closures", "lane_reauthorizations")
    with host.transaction() as db:
        dump = "\n".join(db.iterdump()).encode()
        counts = {name: db.execute(f"SELECT count(*) FROM {name}").fetchone()[0]
                  for name in names}
        counts["last_clock"] = db.execute("SELECT last_clock FROM host_meta").fetchone()[0]
    return {"sha256": hashlib.sha256(dump).hexdigest(), "counts": counts}


def two_stages(root):
    host, owner, request, store, first = fixture(root)
    _, downstream, later = setup_host(root, "CMAD2")
    second = store.submit(downstream, later, make_candidate(root, "second", "CMAD2", "first"),
                          lambda: Clock(now=11.0), execute_gate)
    return host, owner, request, store, first, downstream, later, second
