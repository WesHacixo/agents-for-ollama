# detached-membrane-governance

TypeScript governance spine for the detached membrane SDK (Phase A).

**Python stays the executor runtime.** This package owns manifest checksums, policy compile/verify, layered gates, ZTNA, and fixture-only governance e2e.

## Commands

From this directory:

```bash
bun install
bun run membrane:validate          # typecheck + vitest
bun run membrane:compile-policy
bun run membrane:verify-manifest
bun run membrane:refresh-manifest  # after intentional manifest edits
bun run membrane:verify-policy
bun run membrane:governance-e2e
bun run membrane:ztna issue --identity-ref detached_membrane_agent_local \
  --action membrane_propose --resource cas_return_packet \
  --context-ref cas1_test --out /tmp/ztna.json
```

## TDD fixtures

Gate negative vectors live in `fixtures/gates/` (issue #7). Each file drives `layered-verify.test.ts`.

## Related

- ADR: `docs/portfolio-integration/detached-membrane-governance-ts-architecture.md`
- Epic: https://github.com/WesHacixo/agents-for-ollama/issues/1
- Phase A: https://github.com/WesHacixo/agents-for-ollama/issues/2
