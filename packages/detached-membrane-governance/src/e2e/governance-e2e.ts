import { readFileSync } from "node:fs";
import { join } from "node:path";
import { projectBhrtPacket } from "../executor/bhrt-projection.ts";
import { emitPim0FromProposal } from "../executor/pim0-emit.ts";
import { emitProposalPacket } from "../executor/proposal-emit.ts";
import { bridgeVerificationResult } from "../executor/verification-bridge.ts";
import { evaluateLayers } from "../gates/layered-verify.ts";
import { verifyManifest } from "../manifest/index.ts";
import { MANIFEST_REL, REPO_ROOT, ZTNA_POLICY_REL } from "../paths.ts";
import { issueReceipt, verifyReceipt } from "../ztna/local.ts";

export const GOVERNANCE_E2E_SCHEMA_VERSION = "detached-membrane-governance-e2e-0_1";

export type GovernanceE2EReport = {
  object: "DetachedMembraneGovernanceE2EReport";
  schema_version: typeof GOVERNANCE_E2E_SCHEMA_VERSION;
  accepted: boolean;
  manifest_reasons: string[];
  layered_verification: ReturnType<typeof evaluateLayers>;
  bridged_verification: Record<string, unknown>;
  wyrm_trace_ref: string | null;
  source_packet_id: string;
  fixture_mode: "no_ollama_no_macos_cas";
};

export function runGovernanceE2e(root: string = REPO_ROOT): GovernanceE2EReport {
  const fixture = JSON.parse(
    readFileSync(join(root, "fixtures/detached_membrane/governance_e2e_source_v0.json"), "utf-8"),
  ) as Record<string, string>;
  const hostAck = JSON.parse(
    readFileSync(join(root, "fixtures/detached_membrane/macos_validator_ack_shape.json"), "utf-8"),
  ) as Record<string, unknown>;

  const { ok: manifestOk, reasons: manifestReasons } = verifyManifest(
    join(root, MANIFEST_REL),
    root,
  );
  if (!manifestOk) {
    throw new Error(`manifest verify failed: ${manifestReasons.join("; ")}`);
  }

  const sourcePacketId = fixture.source_packet_id;
  if (!sourcePacketId) {
    throw new Error("governance e2e fixture missing source_packet_id");
  }
  const executorProfileId = fixture.executor_profile_id ?? "python_agents_sdk";
  const packet = emitProposalPacket({
    sourcePacketId,
    executorProfileId,
    summary: fixture.hint ?? "Governance e2e fixture proposal",
    artifactId: "e2efixture0001",
  });

  const receiptPath = join("/tmp", "detached-membrane-governance-e2e-ztna.json");
  const identityRef = fixture.identity_ref ?? "detached_membrane_agent_local";
  const ztnaReceipt = issueReceipt({
    policyPath: join(root, ZTNA_POLICY_REL),
    identityRef,
    action: "membrane_propose",
    resource: "cas_return_packet",
    contextRef: sourcePacketId,
    outPath: receiptPath,
  });

  const ztnaVerifyOk = verifyReceipt({
    receipt: ztnaReceipt,
    action: "membrane_propose",
    resource: "cas_return_packet",
    contextRef: sourcePacketId,
  });

  const ztna = {
    identity_ref: ztnaReceipt.identity_ref,
    policy_decision_ref: ztnaReceipt.decision_ref,
    decision_ttl_seconds: 900,
    receipt_path: receiptPath,
    authority_status: "advisory_only",
    execution_permitted: false,
  };
  packet.ztna = ztna;

  const bridged = bridgeVerificationResult(packet, hostAck);
  const layered = evaluateLayers({
    packet,
    ztna,
    hostAck,
    ztnaVerifyOk,
    policyAssertionsOk: true,
    strictLegality: true,
  });

  const pim0Envelope = emitPim0FromProposal(packet);
  const bhrtProjection = projectBhrtPacket({
    packet,
    verification: bridged,
    ztna,
    pim0Envelope,
    parentReceiptId: ztna.policy_decision_ref,
  });

  return {
    object: "DetachedMembraneGovernanceE2EReport",
    schema_version: GOVERNANCE_E2E_SCHEMA_VERSION,
    accepted: layered.accepted && Boolean(bridged.accepted) && manifestOk,
    manifest_reasons: manifestReasons,
    layered_verification: layered,
    bridged_verification: bridged,
    wyrm_trace_ref: (bhrtProjection.wyrm_trace_ref as string | null) ?? null,
    source_packet_id: sourcePacketId,
    fixture_mode: "no_ollama_no_macos_cas",
  };
}
