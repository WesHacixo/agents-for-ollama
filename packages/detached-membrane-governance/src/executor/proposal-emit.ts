import { randomUUID } from "node:crypto";

const PROPOSAL_SCHEMA_VERSION = "cas-return-0_1";

function returnId(prefix = "detached_membrane", now = new Date()): string {
  const stamp = Math.floor(now.getTime() / 1000);
  return `casreturn_${prefix}_${stamp}`;
}

export type EmitProposalInput = {
  sourcePacketId: string;
  executorProfileId: string;
  summary: string;
  actionTags?: string[];
  artifacts?: string[];
  now?: Date;
  artifactId?: string;
};

export function emitProposalPacket(input: EmitProposalInput): Record<string, unknown> {
  const sourcePacketId = input.sourcePacketId.trim();
  const executorProfileId = input.executorProfileId.trim();
  if (!sourcePacketId) throw new Error("source_packet_id must be non-empty");
  if (!executorProfileId) throw new Error("executor_profile_id must be non-empty");

  let compactSummary = input.summary.trim().replace(/\n/g, " ");
  if (compactSummary.length > 240) {
    compactSummary = `${compactSummary.slice(0, 237)}...`;
  }

  const artifactValues = input.artifacts ?? [
    `proposal:${input.artifactId ?? randomUUID().replace(/-/g, "")}`,
  ];
  const actions = [...(input.actionTags ?? ["detached_membrane:proposal_emit"])];
  actions.push(`summary:${compactSummary}`);

  return {
    object: "CASReturnPacket",
    schema_version: PROPOSAL_SCHEMA_VERSION,
    return_id: returnId("detached_membrane", input.now),
    source_packet_id: sourcePacketId,
    executor_profile_id: executorProfileId,
    executor_family: "local_model_runtime",
    executor_lane: "local_model",
    status: "proposed",
    authority_status: "advisory_only",
    execution_permitted: false,
    actions_taken: actions,
    artifacts: artifactValues,
    validation: { commands_run: [], result: "not_run" },
    deviations_from_scope: ["proposal_only:no_host_apply"],
    risks: ["requires_host_validation", "output_is_proposal_only"],
    proposed_next_state: { macos_session_status: "running" },
    writeback_proposal: { sigmem0: "none", rationale: "" },
    layering_chain: [
      "agents_for_ollama_executor",
      "macos_cas_validate",
      "bhrt_projection",
      "pim0_envelope_index",
    ],
  };
}
