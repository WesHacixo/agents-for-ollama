import { describe, expect, it } from "vitest";
import { verifyStrictLegality } from "./strict-legality.ts";
import { REPO_ROOT } from "../paths.ts";

describe("strict legality", () => {
  it("passes on current repo metadata", () => {
    const result = verifyStrictLegality(REPO_ROOT);
    expect(result.ok).toBe(true);
    expect(result.message).toContain("PASS");
  });
});
