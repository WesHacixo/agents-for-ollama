import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
import { PACKAGE_ROOT, REPO_ROOT } from "../paths.ts";

export type LeakViolation = {
  file: string;
  line: number;
  rule_id: string;
  snippet: string;
  pattern?: string;
};

export type LeakAstRules = {
  forbidden_imports: string[];
  forbidden_markers: string[];
  forbidden_execution_markers: string[];
  required_contracts: string[];
};

export type LeakAstResult = {
  ok: boolean;
  violations: LeakViolation[];
  message: string;
};

const SCANNER = join(PACKAGE_ROOT, "src/gates/leak_ast_scan.py");
const DEFAULT_CORE_REL = "packages/detached_membrane_sdk/detached_membrane_sdk";

export function loadLeakAstRules(root: string = REPO_ROOT): LeakAstRules {
  const assertionsPath = join(
    root,
    "packages/detached_membrane_sdk/policy/generated/verification_assertions.json",
  );
  if (!existsSync(assertionsPath)) {
    throw new Error(
      "FAIL: compiled policy artifacts missing. Run membrane:compile-policy first.",
    );
  }
  const data = JSON.parse(readFileSync(assertionsPath, "utf-8")) as {
    forbidden_imports?: string[];
    forbidden_markers?: string[];
    plane_separation?: { forbidden_execution_markers?: string[] };
    required_contracts?: string[];
  };
  return {
    forbidden_imports: data.forbidden_imports ?? [],
    forbidden_markers: data.forbidden_markers ?? [],
    forbidden_execution_markers: data.plane_separation?.forbidden_execution_markers ?? [],
    required_contracts: data.required_contracts ?? [],
  };
}

export function verifyRequiredContracts(root: string, rules: LeakAstRules): LeakViolation[] {
  const violations: LeakViolation[] = [];
  for (const rel of rules.required_contracts) {
    const path = join(root, rel);
    if (!existsSync(path)) {
      violations.push({
        file: path,
        line: 0,
        rule_id: "missing_contract",
        snippet: rel,
      });
    }
  }
  return violations;
}

export function scanPythonCore(
  coreDir: string,
  rules: LeakAstRules,
): { ok: boolean; violations: LeakViolation[] } {
  const proc = spawnSync("python3", [SCANNER, coreDir], {
    input: JSON.stringify({
      forbidden_imports: rules.forbidden_imports,
      forbidden_markers: rules.forbidden_markers,
      forbidden_execution_markers: rules.forbidden_execution_markers,
    }),
    encoding: "utf-8",
  });

  if (proc.error) {
    throw new Error(`FAIL: leak AST scanner error: ${proc.error.message}`);
  }

  let violations: LeakViolation[] = [];
  if (proc.stdout.trim()) {
    const parsed = JSON.parse(proc.stdout) as { violations?: LeakViolation[] };
    violations = parsed.violations ?? [];
  }

  if (proc.status !== 0 && proc.status !== 1 && violations.length === 0) {
    throw new Error(
      `FAIL: leak AST scanner exited ${proc.status}: ${proc.stderr || proc.stdout}`,
    );
  }

  return { ok: violations.length === 0, violations };
}

export function runLeakAstGate(
  root: string = REPO_ROOT,
  coreRel: string = DEFAULT_CORE_REL,
): LeakAstResult {
  const rules = loadLeakAstRules(root);
  const coreDir = join(root, coreRel);

  console.log("== detached membrane leak gate (AST) ==");
  console.log("-- import boundary check (AST)");
  console.log("-- authority leak keyword check (AST)");
  console.log("-- plane separation assertion check (AST)");

  const coreScan = scanPythonCore(coreDir, rules);
  const contractViolations = verifyRequiredContracts(root, rules);
  const violations = [...coreScan.violations, ...contractViolations];

  if (violations.length > 0) {
    for (const v of violations) {
      console.error(
        `FAIL [${v.rule_id}] ${v.file}:${v.line} ${v.snippet}${v.pattern ? ` (${v.pattern})` : ""}`,
      );
    }
    return {
      ok: false,
      violations,
      message: `FAIL: ${violations.length} leak violation(s) detected`,
    };
  }

  console.log("-- contract coverage check");
  console.log("PASS: no membrane core leaks detected.");
  return { ok: true, violations: [], message: "PASS: no membrane core leaks detected." };
}
