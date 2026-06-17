const VERIFICATION_SCHEMA_VERSION = "detached-membrane-verify-0_1";

export function bridgeVerificationResult(
  packet: Record<string, unknown>,
  hostAck: Record<string, unknown>,
): Record<string, unknown> {
  const accepted = Boolean(hostAck.accepted);
  let errors = hostAck.errors;
  if (!Array.isArray(errors)) {
    errors = errors !== undefined ? [String(errors)] : [];
  }

  return {
    object: "DetachedMembraneVerificationResult",
    schema_version: VERIFICATION_SCHEMA_VERSION,
    accepted,
    errors,
    packet_ref: {
      return_id: packet.return_id,
      source_packet_id: packet.source_packet_id,
      executor_profile_id: packet.executor_profile_id,
      status: packet.status,
    },
  };
}
