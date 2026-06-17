import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { verifyManifest } from "./index.ts";
import { MANIFEST_REL, REPO_ROOT } from "../paths.ts";

describe("manifest verify", () => {
  it("matches declared checksum for repo artifacts", () => {
    const { ok, reasons } = verifyManifest(join(REPO_ROOT, MANIFEST_REL), REPO_ROOT);
    expect(ok).toBe(true);
    expect(reasons.some((r) => r.startsWith("checksum match:"))).toBe(true);
    expect(reasons.some((r) => r.includes("INV.PROPOSAL.ONLY"))).toBe(true);
  });
});
