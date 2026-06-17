import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { evaluateLayers, type LayeredVerifyInput } from "./layered-verify.ts";
import { PACKAGE_ROOT } from "../paths.ts";

type GateFixture = {
  name: string;
  input: LayeredVerifyInput;
  expect: {
    accepted: boolean;
    failedLayerId: string | null;
    reasonContains: string | null;
  };
};

const FIXTURE_DIR = join(PACKAGE_ROOT, "fixtures/gates");
const fixtureFiles = readdirSync(FIXTURE_DIR).filter((f) => f.endsWith(".json"));

describe("layered verify gate fixtures", () => {
  it.each(fixtureFiles)("case %s", (file) => {
    const fixture = JSON.parse(
      readFileSync(join(FIXTURE_DIR, file), "utf-8"),
    ) as GateFixture;
    const result = evaluateLayers(fixture.input);

    expect(result.accepted).toBe(fixture.expect.accepted);
    expect(result.layer_reasons).toHaveLength(5);

    if (fixture.expect.failedLayerId) {
      const failed = result.layer_reasons.find((l) => l.layer_id === fixture.expect.failedLayerId);
      expect(failed?.passed).toBe(false);
      if (fixture.expect.reasonContains) {
        expect(failed?.reason.toLowerCase()).toContain(fixture.expect.reasonContains.toLowerCase());
      }
    } else {
      expect(result.layer_reasons.every((l) => l.passed)).toBe(true);
    }
  });
});
