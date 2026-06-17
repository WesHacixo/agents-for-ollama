import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { POLICY_GENERATED_REL, POLICY_SOURCE_REL, REPO_ROOT } from "../paths.ts";

export type PolicySource = {
  policy_id: string;
  forbidden_imports?: string[];
  forbidden_markers?: string[];
  required_contracts?: string[];
  schema_assertions?: Record<string, unknown>;
  authority_class_requirements?: Record<string, unknown>;
  plane_separation?: Record<string, unknown>;
};

export function compilePolicy(root: string = REPO_ROOT): string {
  const policyPath = join(root, POLICY_SOURCE_REL);
  const genDir = join(root, POLICY_GENERATED_REL);
  const policy = JSON.parse(readFileSync(policyPath, "utf-8")) as PolicySource;

  mkdirSync(genDir, { recursive: true });

  const forbiddenTerms = [
    ...(policy.forbidden_imports ?? []),
    ...(policy.forbidden_markers ?? []),
  ];
  writeFileSync(join(genDir, "leak_patterns.txt"), forbiddenTerms.join("|"), "utf-8");

  const schemaConstraints = {
    policy_id: policy.policy_id,
    schema_assertions: policy.schema_assertions ?? {},
    authority_class_requirements: policy.authority_class_requirements ?? {},
  };
  writeFileSync(join(genDir, "schema_constraints.json"), JSON.stringify(schemaConstraints, null, 2), "utf-8");

  const verificationAssertions = {
    policy_id: policy.policy_id,
    required_contracts: policy.required_contracts ?? [],
    forbidden_imports: policy.forbidden_imports ?? [],
    forbidden_markers: policy.forbidden_markers ?? [],
    plane_separation: policy.plane_separation ?? {},
  };
  writeFileSync(
    join(genDir, "verification_assertions.json"),
    JSON.stringify(verificationAssertions, null, 2),
    "utf-8",
  );

  return policy.policy_id;
}

export function verifyPolicyAssertions(root: string = REPO_ROOT): { ok: boolean; message: string } {
  const genPath = join(root, POLICY_GENERATED_REL, "schema_constraints.json");
  const envelopePath = join(
    root,
    "packages/detached_membrane_sdk/contracts/pim0_event_envelope_v1.json",
  );
  const proposalPath = join(
    root,
    "packages/detached_membrane_sdk/contracts/proposal_packet_schema.json",
  );

  const constraints = JSON.parse(readFileSync(genPath, "utf-8")) as {
    schema_assertions: {
      pim0_required_fields: string[];
      authority_class_enum: string[];
      proposal_status_const: string;
    };
  };
  const assertions = constraints.schema_assertions;
  const envelope = JSON.parse(readFileSync(envelopePath, "utf-8")) as {
    required?: string[];
    properties?: { authority_class?: { enum?: string[] } };
  };
  const proposal = JSON.parse(readFileSync(proposalPath, "utf-8")) as {
    properties?: { status?: { const?: string } };
  };

  const actualRequired = new Set(envelope.required ?? []);
  const missingRequired = assertions.pim0_required_fields.filter((f) => !actualRequired.has(f));
  if (missingRequired.length > 0) {
    return {
      ok: false,
      message: `FAIL: envelope schema missing required fields: ${missingRequired.join(", ")}`,
    };
  }

  const actualEnum = new Set(envelope.properties?.authority_class?.enum ?? []);
  const enumRequired = new Set(assertions.authority_class_enum);
  if (actualEnum.size !== enumRequired.size || [...enumRequired].some((v) => !actualEnum.has(v))) {
    return {
      ok: false,
      message: `FAIL: authority_class enum mismatch`,
    };
  }

  const actualStatus = proposal.properties?.status?.const;
  if (actualStatus !== assertions.proposal_status_const) {
    return {
      ok: false,
      message: `FAIL: proposal status const mismatch: expected=${assertions.proposal_status_const} actual=${actualStatus}`,
    };
  }

  return { ok: true, message: "PASS: compiled policy assertions match live contracts." };
}
