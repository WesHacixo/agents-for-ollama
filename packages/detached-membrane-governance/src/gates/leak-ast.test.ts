import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { loadLeakAstRules, scanPythonCore } from "./leak-ast.ts";
import { PACKAGE_ROOT, REPO_ROOT } from "../paths.ts";

const FIXTURE_DIR = join(PACKAGE_ROOT, "fixtures/leak_ast");
const CORE_DIR = join(REPO_ROOT, "packages/detached_membrane_sdk/detached_membrane_sdk");

describe("leak AST gate", () => {
  const rules = loadLeakAstRules(REPO_ROOT);

  it("passes on production membrane core", () => {
    const result = scanPythonCore(CORE_DIR, rules);
    expect(result.ok).toBe(true);
    expect(result.violations).toHaveLength(0);
  });

  it("passes on clean-only fixture directory", () => {
    const result = scanPythonCore(join(FIXTURE_DIR, "clean_only"), rules);
    expect(result.ok).toBe(true);
    expect(result.violations).toHaveLength(0);
  });

  it("detects forbidden import fixture", () => {
    const result = scanPythonCore(FIXTURE_DIR, rules);
    expect(
      result.violations.some(
        (v) => v.rule_id === "forbidden_import" && v.file.endsWith("violation_import.py"),
      ),
    ).toBe(true);
  });

  it("detects subprocess execution fixture", () => {
    const result = scanPythonCore(FIXTURE_DIR, rules);
    expect(
      result.violations.some(
        (v) =>
          v.rule_id === "forbidden_execution_call" &&
          v.file.endsWith("violation_subprocess.py"),
      ),
    ).toBe(true);
  });

  it("detects forbidden marker fixture", () => {
    const result = scanPythonCore(FIXTURE_DIR, rules);
    expect(
      result.violations.some(
        (v) =>
          (v.rule_id === "forbidden_marker_name" ||
            v.rule_id === "forbidden_marker_string") &&
          v.file.endsWith("violation_marker.py"),
      ),
    ).toBe(true);
  });
});
