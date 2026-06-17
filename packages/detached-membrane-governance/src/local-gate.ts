import { spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { runGovernanceE2e } from "./e2e/governance-e2e.ts";
import { runLeakAstGate } from "./gates/leak-ast.ts";
import { verifyStrictLegality } from "./gates/strict-legality.ts";
import { verifyManifest } from "./manifest/index.ts";
import { compilePolicy, verifyPolicyAssertions } from "./policy/index.ts";
import { MANIFEST_REL, PACKAGE_ROOT, REPO_ROOT, ZTNA_POLICY_REL } from "./paths.ts";
import { issueReceipt, verifyReceipt } from "./ztna/local.ts";

export type LocalGateOptions = {
  root?: string;
  strictLegality?: boolean;
  quick?: boolean;
  skipPythonSdkTests?: boolean;
};

function isQuick(): boolean {
  const v = process.env.MEMBRANE_GATE_QUICK ?? "";
  return v === "1" || v === "true" || v === "yes";
}

function runStep(label: string, fn: () => void): void {
  process.stdout.write(`-- ${label}\n`);
  fn();
}

function runPythonSdkTests(root: string): void {
  process.stdout.write("-- detached membrane sdk tests (python)\n");
  const proc = spawnSync(
    "python3",
    ["-m", "unittest", "-v", "tests/test_detached_membrane_sdk.py"],
    {
      cwd: root,
      stdio: "inherit",
      env: { ...process.env, PYTHONPATH: join(root, "packages/detached_membrane_sdk") },
    },
  );
  if (proc.status !== 0) {
    throw new Error("FAIL: detached membrane sdk python tests");
  }
}

function runTsGovernanceTests(): void {
  process.stdout.write("-- detached membrane governance tests (vitest)\n");
  const proc = spawnSync("bun", ["run", "test"], {
    cwd: PACKAGE_ROOT,
    stdio: "inherit",
  });
  if (proc.status !== 0) {
    throw new Error("FAIL: detached membrane governance vitest suite");
  }
}

function runZtnaGate(root: string): void {
  const receiptDir = mkdtempSync(join(tmpdir(), "membrane-local-gate-ztna-"));
  const receiptPath = join(receiptDir, "ztna-receipt.json");
  const contextRef = process.env.MEMBRANE_ZTNA_CONTEXT ?? "cas1_quality_gate";
  const identityRef = process.env.MEMBRANE_ZTNA_IDENTITY ?? "detached_membrane_agent_local";

  process.stdout.write("-- local ztna issue\n");
  issueReceipt({
    policyPath: join(root, ZTNA_POLICY_REL),
    identityRef,
    action: "membrane_propose",
    resource: "cas_return_packet",
    contextRef,
    outPath: receiptPath,
  });

  process.stdout.write("-- local ztna verify\n");
  const receipt = JSON.parse(readFileSync(receiptPath, "utf-8")) as Parameters<
    typeof verifyReceipt
  >[0]["receipt"];
  const ok = verifyReceipt({
    receipt,
    action: "membrane_propose",
    resource: "cas_return_packet",
    contextRef,
  });
  if (!ok) {
    throw new Error("FAIL: ZTNA receipt invalid");
  }
  console.log("PASS: ZTNA receipt valid");
}

export function runLocalGate(options: LocalGateOptions = {}): void {
  const root = options.root ?? REPO_ROOT;
  const quick = options.quick ?? isQuick();
  const strictLegality = options.strictLegality ?? false;

  console.log("== membrane local gate (TS) ==");

  runStep("compile policy", () => {
    const policyId = compilePolicy(root);
    console.log(`Compiled policy: ${policyId}`);
  });

  runStep("verify policy assertions", () => {
    const result = verifyPolicyAssertions(root);
    console.log(result.message);
    if (!result.ok) throw new Error(result.message);
  });

  runStep("verify manifest checksums", () => {
    const { ok, reasons } = verifyManifest(join(root, MANIFEST_REL), root);
    for (const reason of reasons) console.log(reason);
    if (!ok) throw new Error("FAIL: membrane manifest checksum verification failed");
    console.log("PASS: membrane manifest checksums verified");
  });

  runStep("leak gate (AST)", () => {
    const result = runLeakAstGate(root);
    if (!result.ok) throw new Error(result.message);
  });

  runStep("local ztna gate", () => runZtnaGate(root));

  if (!quick) {
    runStep("governance e2e (fixture-only)", () => {
      const report = runGovernanceE2e(root);
      if (!report.accepted) {
        writeFileSync(
          join(tmpdir(), "membrane-governance-e2e-fail.json"),
          JSON.stringify(report, null, 2),
        );
        throw new Error("FAIL: governance e2e not accepted");
      }
      console.log("PASS: governance e2e accepted");
    });
  } else {
    process.stdout.write("SKIP: governance e2e (MEMBRANE_GATE_QUICK=1)\n");
  }

  runTsGovernanceTests();

  if (!quick && !options.skipPythonSdkTests) {
    runPythonSdkTests(root);
  } else if (quick) {
    process.stdout.write("SKIP: python sdk tests (MEMBRANE_GATE_QUICK=1)\n");
  }

  if (strictLegality) {
    runStep("strict legality checks", () => {
      const result = verifyStrictLegality(root);
      console.log(result.message);
      if (!result.ok) throw new Error(result.message);
    });
  }

  console.log("PASS: membrane local gate complete.");
}
