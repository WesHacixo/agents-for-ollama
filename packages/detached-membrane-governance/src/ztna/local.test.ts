import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { issueReceipt, verifyReceipt } from "./local.ts";
import { REPO_ROOT, ZTNA_POLICY_REL } from "../paths.ts";

const FIXED_NOW = new Date("2026-06-17T12:00:00.000Z");
const clock = () => FIXED_NOW;

describe("ztna local", () => {
  it("issues and verifies a membrane_propose receipt", () => {
    const receipt = issueReceipt({
      policyPath: join(REPO_ROOT, ZTNA_POLICY_REL),
      identityRef: "detached_membrane_agent_local",
      action: "membrane_propose",
      resource: "cas_return_packet",
      contextRef: "cas1_ztna_test",
      clock,
    });

    expect(receipt.decision).toBe("allow");
    expect(receipt.decision_ref).toMatch(/^ztna_decision_[a-f0-9]{16}$/);

    expect(
      verifyReceipt({
        receipt,
        action: "membrane_propose",
        resource: "cas_return_packet",
        contextRef: "cas1_ztna_test",
        clock,
      }),
    ).toBe(true);
  });

  it("rejects expired receipt", () => {
    const receipt = issueReceipt({
      policyPath: join(REPO_ROOT, ZTNA_POLICY_REL),
      identityRef: "detached_membrane_agent_local",
      action: "membrane_propose",
      resource: "cas_return_packet",
      contextRef: "cas1_ztna_expired",
      clock,
    });

    const later = () => new Date(FIXED_NOW.getTime() + 901_000);
    expect(
      verifyReceipt({
        receipt,
        action: "membrane_propose",
        resource: "cas_return_packet",
        contextRef: "cas1_ztna_expired",
        clock: later,
      }),
    ).toBe(false);
  });

  it("rejects action mismatch", () => {
    const receipt = issueReceipt({
      policyPath: join(REPO_ROOT, ZTNA_POLICY_REL),
      identityRef: "detached_membrane_agent_local",
      action: "membrane_propose",
      resource: "cas_return_packet",
      contextRef: "cas1_ztna_action",
      clock,
    });

    expect(
      verifyReceipt({
        receipt,
        action: "other_action",
        resource: "cas_return_packet",
        contextRef: "cas1_ztna_action",
        clock,
      }),
    ).toBe(false);
  });
});
