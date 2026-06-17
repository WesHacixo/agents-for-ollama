import { readFileSync } from "node:fs";
import { join } from "node:path";

export function verifyStrictLegality(root: string): { ok: boolean; message: string } {
  const adoption = readFileSync(
    join(root, "docs/detached-membrane-policy-adoption.md"),
    "utf-8",
  );
  if (!adoption.includes("uber_policy: detached_membrane_policy_v1@0.1.0")) {
    return { ok: false, message: "FAIL: missing detached membrane uber_policy stamp" };
  }

  const registry = readFileSync(
    join(root, "packages/detached_membrane_sdk/policy/policy_registry.yaml"),
    "utf-8",
  );
  if (!registry.includes("detached_membrane_policy_v1@0.1.0")) {
    return { ok: false, message: "FAIL: policy registry stamp mismatch" };
  }

  const constraints = JSON.parse(
    readFileSync(
      join(root, "packages/detached_membrane_sdk/policy/generated/schema_constraints.json"),
      "utf-8",
    ),
  ) as { schema_assertions?: { proposal_requires_lineage?: boolean } };

  if (!constraints.schema_assertions?.proposal_requires_lineage) {
    return { ok: false, message: "FAIL: strict legality requires proposal lineage assertion" };
  }

  return { ok: true, message: "PASS: strict legality metadata checks" };
}
