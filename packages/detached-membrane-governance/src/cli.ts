import { compilePolicy, verifyPolicyAssertions } from "./policy/index.ts";
import { verifyManifest, refreshDeclaredChecksum } from "./manifest/index.ts";
import { runGovernanceE2e } from "./e2e/governance-e2e.ts";
import { issueReceipt, verifyReceipt } from "./ztna/local.ts";
import { MANIFEST_REL, REPO_ROOT, ZTNA_POLICY_REL } from "./paths.ts";
import { join } from "node:path";

const [cmd, ...rest] = process.argv.slice(2);

function usage(): never {
  console.error(`Usage: bun src/cli.ts <command>

Commands:
  compile-policy
  verify-manifest
  refresh-manifest
  verify-policy
  governance-e2e
  ztna issue|verify [options]
`);
  process.exit(1);
}

function parseFlags(args: string[]): Record<string, string> {
  const flags: Record<string, string> = {};
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg?.startsWith("--") && args[i + 1]) {
      flags[arg.slice(2)] = args[++i] as string;
    }
  }
  return flags;
}

async function main(): Promise<number> {
  if (!cmd) usage();

  switch (cmd) {
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
    case "ztna": {
      const sub = rest[0];
      const flags = parseFlags(rest.slice(1));
      if (sub === "issue") {
        const receipt = issueReceipt({
          policyPath: flags.policy ?? join(REPO_ROOT, ZTNA_POLICY_REL),
          identityRef: flags["identity-ref"] ?? "detached_membrane_agent_local",
          action: flags.action ?? "membrane_propose",
          resource: flags.resource ?? "cas_return_packet",
          contextRef: flags["context-ref"] ?? "",
          outPath: flags.out,
        });
        console.log(JSON.stringify(receipt, null, 2));
        return 0;
      }
      if (sub === "verify") {
        const receiptPath = flags.receipt;
        if (!receiptPath) {
          console.error("FAIL: --receipt required");
          return 1;
        }
        const receipt = JSON.parse(await Bun.file(receiptPath).text());
        const ok = verifyReceipt({
          receipt,
          action: flags.action ?? "membrane_propose",
          resource: flags.resource ?? "cas_return_packet",
          contextRef: flags["context-ref"] ?? "",
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
