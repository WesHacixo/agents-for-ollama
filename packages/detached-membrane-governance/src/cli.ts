import { compilePolicy, verifyPolicyAssertions } from "./policy/index.ts";
import { verifyManifest, refreshDeclaredChecksum } from "./manifest/index.ts";
import { runGovernanceE2e } from "./e2e/governance-e2e.ts";
import { issueReceipt, verifyReceipt } from "./ztna/local.ts";
import { runLocalGate } from "./local-gate.ts";
import { buildPortfolioDigest } from "./cli/portfolio-digest.ts";
import { MANIFEST_REL, REPO_ROOT, ZTNA_POLICY_REL } from "./paths.ts";
import { join } from "node:path";

const [cmd, ...rest] = process.argv.slice(2);

function usage(): never {
  console.error(`Usage: bun src/cli.ts <command>

Commands:
  local-gate [--strict-legality]
  compile-policy
  verify-manifest
  refresh-manifest
  verify-policy
  governance-e2e
  portfolio-digest
  ztna issue|verify [options]

Env:
  MEMBRANE_GATE_QUICK=1     skip governance e2e + python sdk tests
`);
  process.exit(1);
}

function parseFlags(args: string[]): Record<string, string | boolean> {
  const flags: Record<string, string | boolean> = {};
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === "--strict-legality") {
      flags["strict-legality"] = true;
      continue;
    }
    if (arg?.startsWith("--") && args[i + 1] && !args[i + 1]?.startsWith("--")) {
      flags[arg.slice(2)] = args[++i] as string;
    }
  }
  return flags;
}

async function main(): Promise<number> {
  if (!cmd) usage();

  switch (cmd) {
    case "local-gate": {
      const flags = parseFlags(rest);
      try {
        runLocalGate({
          strictLegality: Boolean(flags["strict-legality"]),
        });
        return 0;
      } catch (err) {
        console.error(err instanceof Error ? err.message : String(err));
        return 1;
      }
    }
    case "compile-policy": {
      const policyId = compilePolicy(REPO_ROOT);
      console.log(`Compiled policy: ${policyId}`);
      return 0;
    }
    case "verify-manifest": {
      const { ok, reasons } = verifyManifest(join(REPO_ROOT, MANIFEST_REL), REPO_ROOT);
      for (const reason of reasons) console.log(reason);
      if (!ok) {
        console.error("FAIL: membrane manifest checksum verification failed");
        return 1;
      }
      console.log("PASS: membrane manifest checksums verified");
      return 0;
    }
    case "refresh-manifest": {
      const checksum = refreshDeclaredChecksum(join(REPO_ROOT, MANIFEST_REL), REPO_ROOT);
      console.log(`updated declared_checksum=${checksum}`);
      return 0;
    }
    case "verify-policy": {
      compilePolicy(REPO_ROOT);
      const result = verifyPolicyAssertions(REPO_ROOT);
      console.log(result.message);
      return result.ok ? 0 : 1;
    }
    case "governance-e2e": {
      const report = runGovernanceE2e(REPO_ROOT);
      console.log(JSON.stringify(report, null, 2));
      return report.accepted ? 0 : 1;
    }
    case "portfolio-digest": {
      const flags = parseFlags(rest);
      const digestRoot = process.env.AGENTS_FOR_OLLAMA_ROOT ?? REPO_ROOT;
      const digest = buildPortfolioDigest({
        root: digestRoot,
        verify: {
          quality_gate: String(flags["quality-gate"] ?? process.env.MEMBRANE_DIGEST_QUALITY_GATE ?? "unknown"),
          unit_tests: String(flags["unit-tests"] ?? process.env.MEMBRANE_DIGEST_UNIT_TESTS ?? "unknown"),
          python_agents_smoke: String(
            flags["python-agents-smoke"] ?? process.env.MEMBRANE_DIGEST_PYTHON_AGENTS_SMOKE ?? "skipped",
          ),
          ts_governance: String(
            flags["ts-governance"] ?? process.env.MEMBRANE_DIGEST_TS_GOVERNANCE ?? "unknown",
          ),
        },
      });
      console.log(JSON.stringify(digest, null, 2));
      return 0;
    }
    case "ztna": {
      const sub = rest[0];
      const flags = parseFlags(rest.slice(1));
      if (sub === "issue") {
        const receipt = issueReceipt({
          policyPath: (flags.policy as string) ?? join(REPO_ROOT, ZTNA_POLICY_REL),
          identityRef: (flags["identity-ref"] as string) ?? "detached_membrane_agent_local",
          action: (flags.action as string) ?? "membrane_propose",
          resource: (flags.resource as string) ?? "cas_return_packet",
          contextRef: (flags["context-ref"] as string) ?? "",
          outPath: flags.out as string | undefined,
        });
        console.log(JSON.stringify(receipt, null, 2));
        return 0;
      }
      if (sub === "verify") {
        const receiptPath = flags.receipt as string | undefined;
        if (!receiptPath) {
          console.error("FAIL: --receipt required");
          return 1;
        }
        const receipt = JSON.parse(await Bun.file(receiptPath).text());
        const ok = verifyReceipt({
          receipt,
          action: (flags.action as string) ?? "membrane_propose",
          resource: (flags.resource as string) ?? "cas_return_packet",
          contextRef: (flags["context-ref"] as string) ?? "",
        });
        if (!ok) {
          console.log("FAIL: ZTNA receipt invalid");
          return 1;
        }
        console.log("PASS: ZTNA receipt valid");
        return 0;
      }
      usage();
    }
    default:
      usage();
  }
}

const code = await main();
process.exit(code);
