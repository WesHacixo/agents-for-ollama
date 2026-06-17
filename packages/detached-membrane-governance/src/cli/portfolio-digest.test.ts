import { describe, expect, it } from "vitest";
import { buildPortfolioDigest } from "./portfolio-digest.ts";
import { REPO_ROOT } from "../paths.ts";

describe("portfolio digest", () => {
  it("emits AgentsForOllamaPortfolioDigestV0 shape", () => {
    const digest = buildPortfolioDigest({
      root: REPO_ROOT,
      verify: {
        quality_gate: "pass",
        unit_tests: "pass",
        python_agents_smoke: "skipped_ollama_down",
        ts_governance: "pass",
      },
    });

    expect(digest.object).toBe("AgentsForOllamaPortfolioDigestV0");
    expect(digest.authority_status).toBe("projection_not_truth");
    expect(digest.bridge_objects).toContain("cas_return_packet_v0_1");
    expect(digest.verify.ts_governance).toBe("pass");
    expect(digest.git_head).toMatch(/^[0-9a-f]+$/);
  });
});
