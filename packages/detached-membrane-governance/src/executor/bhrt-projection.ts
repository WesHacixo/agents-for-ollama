import { createHash } from "node:crypto";

const PROJECTION_SCHEMA_VERSION = "bhrt-projection-0_2";

const DEFAULT_LAYERING_CHAIN = [
  "cloudflare_edge",
  "dmi_membrane_pim0_worker",
  "mcp_tunnel_transport",
  "secgate_wyrm_admission",
  "bhrt_runtime_semantics",
  "supabase_ledger",
];

export function deriveWyrmTraceRef(policyDecisionRef: string | null | undefined): string | null {
  if (!policyDecisionRef) return null;
  const digest = createHash("sha256").update(policyDecisionRef).digest("hex").slice(0, 24);
  return `wyrm-${digest}`;
}

export function projectBhrtPacket(input: {
  packet: Record<string, unknown>;
  verification?: Record<string, unknown> | null;
  ztna?: Record<string, unknown> | null;
  pim0Envelope?: Record<string, unknown> | null;
  wyrmTraceRefs?: string[];
  parentReceiptId?: string | null;
}): Record<string, unknown> {
  const ztnaData = (input.ztna ?? input.packet.ztna ?? {}) as Record<string, unknown>;
  const policyDecisionRef = ztnaData.policy_decision_ref as string | undefined;
  const accepted = Boolean(input.verification?.accepted);
  let traceRefs = input.wyrmTraceRefs ?? [];
  if (traceRefs.length === 0) {
    const derived = deriveWyrmTraceRef(policyDecisionRef);
    if (derived) traceRefs = [derived];
  }

  return {
    object: "BHRTDetachedMembraneProjection",
    schema_version: PROJECTION_SCHEMA_VERSION,
    authority_status: "advisory_only",
    execution_permitted: false,
    authority: {
      authority_class: "proposal",
      policy_decision_ref: policyDecisionRef,
      advisory_only: true,
    },
    lineage: {
      source_packet_id: input.packet.source_packet_id,
      return_id: input.packet.return_id,
      parent_receipt_id: input.parentReceiptId ?? null,
    },
    layering_chain: DEFAULT_LAYERING_CHAIN,
    lane_separation: {
      dmi_ingress: "pim0.blue-hand.org",
      nexus_advisory: "api.bluehand.dev / mcp.bluehand.dev",
      public_implement_bridge: "docs.bluehand.dev",
      wyrm_admission: "local wyrm_gate (T1 lease broker)",
    },
    coverage_snapshot: {
      actions_taken_count: (input.packet.actions_taken as unknown[] | undefined)?.length ?? 0,
      artifacts_count: (input.packet.artifacts as unknown[] | undefined)?.length ?? 0,
      host_accepted: accepted,
    },
    state_delta_refs: input.packet.artifacts ?? [],
    external_lineage_refs: policyDecisionRef ? [policyDecisionRef] : [],
    wyrm_trace_refs: traceRefs,
    wyrm_trace_ref: traceRefs[0] ?? null,
    pim0_envelope_ref: (input.pim0Envelope?.envelope_id as string | undefined) ?? null,
    receipt: {
      boundary: "detached_membrane.local",
      decision: accepted ? "admitted" : "denied",
      execution_permitted: false,
      reason_code: accepted ? "proposal_only" : "host_validation_failed",
    },
  };
}
