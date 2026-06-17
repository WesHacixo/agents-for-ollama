import { createHash, randomUUID } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";

export type ZtnaPolicy = {
  policy_id?: string;
  ttl_seconds_default?: number;
  default_decision?: string;
  identity?: { trusted_prefixes?: string[] };
  rules?: Array<{
    action?: string;
    allowed_resources?: string[];
    allow?: boolean;
  }>;
};

export type ZtnaReceipt = {
  object: "LocalZTNADecisionReceipt";
  schema_version: "local-ztna-0_1";
  policy_id: string;
  decision_ref: string;
  decision: string;
  identity_ref: string;
  action: string;
  resource: string;
  context_ref: string;
  issued_at: string;
  expires_at: string;
  token_id: string;
};

export type ZtnaClock = () => Date;

const defaultClock: ZtnaClock = () => new Date();

function isoNow(clock: ZtnaClock): string {
  return clock().toISOString();
}

/** Python-compatible offset-aware isoformat for expires_at hashing. */
function pythonIsoExpires(secondsFromNow: number, clock: ZtnaClock): string {
  const d = new Date(clock().getTime() + secondsFromNow * 1000);
  return d.toISOString().replace(/\.\d{3}Z$/, "+00:00").replace("Z", "+00:00");
}

function parseIso(ts: string): Date {
  return new Date(ts.replace("Z", "+00:00"));
}

function loadPolicy(policyPath: string): ZtnaPolicy {
  return JSON.parse(readFileSync(policyPath, "utf-8")) as ZtnaPolicy;
}

function policyAllows(policy: ZtnaPolicy, action: string, resource: string): boolean {
  for (const rule of policy.rules ?? []) {
    if (rule.action !== action) continue;
    if (rule.allowed_resources?.includes(resource) && rule.allow) return true;
  }
  return false;
}

function identityAllowed(policy: ZtnaPolicy, identityRef: string): boolean {
  const prefixes = policy.identity?.trusted_prefixes ?? [];
  return prefixes.some((prefix) => identityRef.startsWith(prefix));
}

export type IssueReceiptInput = {
  policyPath: string;
  identityRef: string;
  action: string;
  resource: string;
  contextRef: string;
  outPath?: string;
  clock?: ZtnaClock;
};

export function issueReceipt(input: IssueReceiptInput): ZtnaReceipt {
  const clock = input.clock ?? defaultClock;
  const policy = loadPolicy(input.policyPath);
  const allowed =
    identityAllowed(policy, input.identityRef) &&
    policyAllows(policy, input.action, input.resource);
  const ttl = policy.ttl_seconds_default ?? 900;
  const expiresAt = pythonIsoExpires(ttl, clock);
  const decision = allowed ? "allow" : (policy.default_decision ?? "deny");

  const base = `${input.identityRef}|${input.action}|${input.resource}|${input.contextRef}|${decision}|${expiresAt}`;
  const decisionRef =
    "ztna_decision_" + createHash("sha256").update(base).digest("hex").slice(0, 16);

  const receipt: ZtnaReceipt = {
    object: "LocalZTNADecisionReceipt",
    schema_version: "local-ztna-0_1",
    policy_id: policy.policy_id ?? "unknown",
    decision_ref: decisionRef,
    decision,
    identity_ref: input.identityRef,
    action: input.action,
    resource: input.resource,
    context_ref: input.contextRef,
    issued_at: isoNow(clock),
    expires_at: expiresAt,
    token_id: `ztna_${randomUUID().replace(/-/g, "").slice(0, 12)}`,
  };

  if (input.outPath) {
    writeFileSync(input.outPath, `${JSON.stringify(receipt, null, 2)}\n`, "utf-8");
  }
  if (!allowed) {
    throw new Error("ZTNA policy denied membrane_propose for cas_return_packet");
  }
  return receipt;
}

export type VerifyReceiptInput = {
  receipt: ZtnaReceipt;
  action: string;
  resource: string;
  contextRef?: string;
  clock?: ZtnaClock;
};

export function verifyReceipt(input: VerifyReceiptInput): boolean {
  const clock = input.clock ?? defaultClock;
  const now = clock();
  const expiresAt = parseIso(input.receipt.expires_at);

  if (input.receipt.decision !== "allow") return false;
  if (now > expiresAt) return false;
  if (input.receipt.action !== input.action) return false;
  if (input.receipt.resource !== input.resource) return false;
  if (input.contextRef && input.receipt.context_ref !== input.contextRef) return false;
  return true;
}
