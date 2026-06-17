export const LAYERED_VERIFY_SCHEMA_VERSION = "detached-membrane-layered-verify-0_1";

export type LayerReason = {
  layer_id: string;
  name: string;
  passed: boolean;
  reason: string;
  details?: Record<string, unknown>;
};

export type CasReturnPacket = Record<string, unknown> & {
  object?: string;
  status?: string;
  authority_status?: string;
  execution_permitted?: boolean;
  source_packet_id?: string;
  layering_chain?: string[];
  actions_taken?: string[];
  ztna?: ZtnaAttachment;
};

export type ZtnaAttachment = {
  policy_decision_ref?: string;
  receipt_path?: string;
  decision_ttl_seconds?: number;
};

export type HostAck = {
  accepted?: boolean;
  errors?: unknown[];
};

export type LayeredVerifyInput = {
  packet: CasReturnPacket;
  ztna?: ZtnaAttachment;
  hostAck?: HostAck | null;
  ztnaVerifyOk?: boolean | null;
  policyAssertionsOk?: boolean | null;
  strictLegality?: boolean;
};

export type LayeredVerification = {
  object: "DetachedMembraneLayeredVerification";
  schema_version: typeof LAYERED_VERIFY_SCHEMA_VERSION;
  accepted: boolean;
  layer_reasons: LayerReason[];
};

function layer(
  layerId: string,
  name: string,
  passed: boolean,
  reason: string,
  details?: Record<string, unknown>,
): LayerReason {
  const entry: LayerReason = { layer_id: layerId, name, passed, reason };
  if (details) entry.details = details;
  return entry;
}

export function evaluateLayers(input: LayeredVerifyInput): LayeredVerification {
  const ztna = input.ztna ?? input.packet.ztna ?? {};
  const layers: LayerReason[] = [];

  const contractOk =
    input.packet.object === "CASReturnPacket" &&
    input.packet.status === "proposed" &&
    input.packet.authority_status === "advisory_only" &&
    input.packet.execution_permitted === false &&
    Boolean(input.packet.source_packet_id);

  layers.push(
    layer(
      "L0",
      "contracts",
      contractOk,
      contractOk
        ? "proposal packet satisfies advisory-only contract surface"
        : "packet missing required proposal-only contract fields",
      {
        object: input.packet.object,
        status: input.packet.status,
        authority_status: input.packet.authority_status,
        execution_permitted: input.packet.execution_permitted,
      },
    ),
  );

  let policyPassed: boolean;
  let policyReason: string;
  if (input.policyAssertionsOk === undefined || input.policyAssertionsOk === null) {
    policyPassed = true;
    policyReason = "policy assertions not evaluated in this path";
  } else {
    policyPassed = input.policyAssertionsOk;
    policyReason = policyPassed
      ? "compiled policy assertions match live contracts"
      : "compiled policy assertions failed";
  }
  layers.push(layer("L1", "policy_compiler", policyPassed, policyReason));

  const ztnaPresent = Boolean(ztna.policy_decision_ref) && Boolean(ztna.receipt_path);
  let ztnaPassed: boolean;
  let ztnaReason: string;
  if (input.ztnaVerifyOk === undefined || input.ztnaVerifyOk === null) {
    ztnaPassed = ztnaPresent;
    ztnaReason = ztnaPresent
      ? "ztna receipt metadata present"
      : "ztna receipt metadata missing";
  } else {
    ztnaPassed = ztnaPresent && input.ztnaVerifyOk;
    ztnaReason = ztnaPassed
      ? "ztna receipt verified for membrane_propose action"
      : "ztna receipt verification failed or metadata missing";
  }
  layers.push(
    layer("L2", "ztna_gate", ztnaPassed, ztnaReason, {
      policy_decision_ref: ztna.policy_decision_ref,
    }),
  );

  let hostPassed: boolean;
  let hostReason: string;
  if (input.hostAck === undefined || input.hostAck === null) {
    hostPassed = false;
    hostReason = "host validator acknowledgement not available";
  } else {
    hostPassed = Boolean(input.hostAck.accepted);
    const errors = input.hostAck.errors ?? [];
    hostReason = hostPassed
      ? "host validator accepted proposal packet"
      : `host validator rejected proposal: ${JSON.stringify(errors)}`;
  }
  layers.push(layer("L3", "host_validation", hostPassed, hostReason, {
    accepted: input.hostAck?.accepted ?? null,
  }));

  const lineageReady =
    Boolean(input.packet.layering_chain?.length) &&
    Boolean(input.packet.actions_taken?.length);

  let strictOk: boolean;
  let lineageReason: string;
  if (input.strictLegality) {
    strictOk =
      lineageReady &&
      Boolean(ztna.policy_decision_ref) &&
      Number(ztna.decision_ttl_seconds ?? 0) > 0;
    lineageReason = strictOk
      ? "strict legality lineage and ztna TTL satisfied"
      : "strict legality requirements not met";
  } else {
    strictOk = lineageReady;
    lineageReason = strictOk
      ? "projection lineage fields present"
      : "missing layering_chain or actions_taken for projection";
  }
  layers.push(
    layer("L4", "lineage_projection", strictOk, lineageReason, {
      layering_chain_len: input.packet.layering_chain?.length ?? 0,
    }),
  );

  return {
    object: "DetachedMembraneLayeredVerification",
    schema_version: LAYERED_VERIFY_SCHEMA_VERSION,
    accepted: layers.every((l) => l.passed),
    layer_reasons: layers,
  };
}
