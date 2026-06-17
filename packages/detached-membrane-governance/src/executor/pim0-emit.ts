const PIM0_ENVELOPE_VERSION = "PIM0_EVENT_ENVELOPE_V1";
const VALID_AUTHORITY_CLASSES = new Set([
  "advisory",
  "proposal",
  "governed",
  "canonical",
  "presentation_only",
]);

export function adaptEventEnvelope(input: {
  sourceRepo: string;
  sourceObjectType: string;
  sourceSchemaRef: string;
  sourceObjectRef: string;
  sourceHash: string;
  authorityClass: string;
  lineageRef: string;
  policyVersion: string;
  mutationAllowed: boolean;
  receiptRef: string | null;
  envelopeId: string;
  observedAt?: string;
  now?: Date;
}): Record<string, unknown> {
  const required: Record<string, string> = {
    source_repo: input.sourceRepo,
    source_object_type: input.sourceObjectType,
    source_schema_ref: input.sourceSchemaRef,
    source_object_ref: input.sourceObjectRef,
    source_hash: input.sourceHash,
    lineage_ref: input.lineageRef,
    policy_version: input.policyVersion,
    envelope_id: input.envelopeId,
  };
  for (const [key, value] of Object.entries(required)) {
    if (!value.trim()) throw new Error(`${key} must be non-empty`);
  }
  if (!VALID_AUTHORITY_CLASSES.has(input.authorityClass)) {
    throw new Error(`authority_class must be one of: ${[...VALID_AUTHORITY_CLASSES].sort().join(", ")}`);
  }

  return {
    envelope_version: PIM0_ENVELOPE_VERSION,
    envelope_id: input.envelopeId,
    source_repo: input.sourceRepo,
    source_object_type: input.sourceObjectType,
    source_schema_ref: input.sourceSchemaRef,
    source_object_ref: input.sourceObjectRef,
    source_hash: input.sourceHash,
    authority_class: input.authorityClass,
    lineage_ref: input.lineageRef,
    policy_version: input.policyVersion,
    mutation_allowed: Boolean(input.mutationAllowed),
    receipt_ref: input.receiptRef,
    observed_at: input.observedAt ?? (input.now ?? new Date()).toISOString(),
  };
}

export function emitPim0FromProposal(
  packet: Record<string, unknown>,
  options?: { envelopeId?: string; now?: Date },
): Record<string, unknown> {
  const returnId = String(packet.return_id ?? "unknown_return");
  const sourcePacketId = String(packet.source_packet_id ?? "unknown_source");
  const envelopeId = options?.envelopeId ?? `evt_dm_${returnId}`;
  const ztna = (packet.ztna ?? {}) as Record<string, unknown>;

  return adaptEventEnvelope({
    sourceRepo: "agents-for-ollama",
    sourceObjectType: "CASReturnPacket",
    sourceSchemaRef: "cas-return-0_1",
    sourceObjectRef: returnId,
    sourceHash: `b3:${returnId}`,
    authorityClass: "presentation_only",
    lineageRef: sourcePacketId,
    policyVersion: "detached-membrane-policy-v1",
    mutationAllowed: false,
    receiptRef: (ztna.policy_decision_ref as string | undefined) ?? null,
    envelopeId,
    now: options?.now,
  });
}
