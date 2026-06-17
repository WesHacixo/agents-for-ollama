import { describe, expect, it } from "vitest";
import { runGovernanceE2e } from "./governance-e2e.ts";
import { REPO_ROOT } from "../paths.ts";

describe("governance e2e", () => {
  it("passes fixture-only loop without Ollama or MacOS-CAS", () => {
    const report = runGovernanceE2e(REPO_ROOT);
    expect(report.accepted).toBe(true);
    expect(report.fixture_mode).toBe("no_ollama_no_macos_cas");
    expect(report.layered_verification.accepted).toBe(true);
    expect(report.wyrm_trace_ref?.startsWith("wyrm-")).toBe(true);
    expect(report.layered_verification.layer_reasons).toHaveLength(5);
  });
});
