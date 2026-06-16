uber_policy: detached_membrane_policy_v1@0.1.0

# Detached membrane policy adoption

Atlas-style policy adoption metadata for `agents-for-ollama` detached membrane core.

## Registry entry

```yaml
id: detached_membrane_policy_v1
version: "0.1.0"
uber_policy_stamp: detached_membrane_policy_v1@0.1.0
canonical_doc: docs/detached-membrane-policy-adoption.md
adopted_by:
  - packages/detached_membrane_sdk/policy/policy_source.json
  - scripts/membrane_quality_gate.sh
  - scripts/check_membrane_leaks.sh
  - scripts/verify_membrane_policy.sh
enforce_local:
  - scripts/membrane_quality_gate.sh
  - scripts/check_membrane_leaks.sh
```

## Scope

- Detached membrane core contract compatibility
- Authority leak prevention
- Local ZTNA decision linkage
- Strict legality checks for proposal packets and verification output
