# P1 bounded lane MCP interface

The transport uses the official Model Context Protocol Python SDK, pinned to
`mcp==2.3.0`. The upstream SDK documentation and installed implementation were
reviewed before binding its server/client APIs:
https://github.com/modelcontextprotocol/python-sdk

The host launches one stdio process per trusted `LaneBinding`. Its frozen strict
contract contains identity (principal, role, lane, stage, credential reference),
task/revision, authority-store path, root, destination, and policy. None of these
are MCP tool arguments. There is no anonymous/default binding or wire API to
assign tasks, create grants, change credentials, or revoke another principal.

```bash
uv run python -m hmt_rnd.mcp_stdio /host/protected/lane-binding.json
```

The config is opened once using `O_NOFOLLOW|O_CLOEXEC|O_NONBLOCK`; the same open
descriptor is checked with `fstat` for regular-file type, current server owner,
and absence of group/world write permission, then read with a 64 KiB bound.
This closes the prior `stat(path)` then `open(path)` replacement race. A symlink
is rejected, and replacing the pathname after open does not change its bytes.

The trusted launcher must protect the config's parent directories, authority DB,
root filesystem, and server process from the MCP client. Unix ownership checks
do not authenticate a malicious same-UID host or isolate an adversarial kernel.
Do not run a privileged stdio server with client-selected launch configuration.
No remote HTTP authentication scheme or bearer-token endpoint is claimed here.

## Discovery, invocation, and tools

Both discovery and invocation use the existing derivative `host_admission.admit`
boundary. It intersects current grant/revocation, all identity fields, task and
revision, policy/epoch, time/freshness, root, and destination. The trusted binding's
policy must also remain current. Hidden or stale cached tools cannot bypass calls.
SDK clients may cache discovery; qualification tests explicitly refresh discovery
and also try the previously cached operation after revocation.

Only two operations are exposed:

| Tool | Input | Output and authority ceiling |
| --- | --- | --- |
| `inspect_context` | Empty closed object | Current admitted identity/task metadata; no credential value, root path, or effect grant |
| `validate_handoff` | One bounded closed handoff | Shape validity, reported status, `acceptance_granted=false`, and `effect_authority=NONE` |

The handoff role/task must match the trusted launch binding. Caller-reported
`validation_status=pass` is data; it cannot seal a stage, accept a package, or
complete a task. No custody reconciliation, arbitrary path/file reader, shell,
code executor, lifecycle mutation, or host-administration tool is exposed.
Lifecycle submission/reopening waits for qualified host-owned stage evaluators.

Tools mutate no task, artifact, or lifecycle state. The common authority boundary
does checkpoint its trusted clock in the host DB, so the server does not advertise
a blanket `readOnlyHint` implying zero persistence. Handoff evaluation is stateless
apart from that shared admission checkpoint.

A bounded input stream rejects stdio frames over 65,536 bytes before the SDK
JSON parser. Tool arguments also have a separate 64 KiB serialized bound, with
strict fields and finite handoff text/list limits. The SDK's stdout transport
protects protocol output from stray application prints. The customized stream
runner uses the SDK's private low-level handle only in `mcp_server.py`; keep the
exact SDK pin and rerun process tests before any SDK version update.

## Verification and limits

Actual SDK `Client` sessions spawn the module over stdio. Tests exercise tool
discovery, direct/MCP parity, malformed and hidden calls, forged principal and
admission fields, unauthenticated/mismatched identity, revoked credentials,
changed task revision and policy, handoff scope, and exact launch-file boundaries.
A separate real process test sends an oversized frame and proves fail-closed exit.
The descriptor-replacement test preserves the initially opened binding.

This is a scoped P1 protocol tracer, not full lane readiness. Live vendor services,
production credentials, deployment isolation, platform portability, lifecycle
effects, and stage gate evaluators remain separate qualification obligations.
No supplied HMT reference package is imported or required at runtime.
