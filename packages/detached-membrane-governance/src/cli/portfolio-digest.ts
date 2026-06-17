import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { join } from "node:path";

export type PortfolioDigestV0 = {
  object: "AgentsForOllamaPortfolioDigestV0";
  authority_status: "projection_not_truth";
  repo_root: string;
  git_head: string | null;
  verify: {
    quality_gate: string;
    unit_tests: string;
    python_agents_smoke: string;
    ts_governance: string;
  };
  bridge_objects: string[];
  critical_path: string;
  posture: string;
};

export type PortfolioDigestInput = {
  root: string;
  verify?: Partial<PortfolioDigestV0["verify"]>;
};

function gitShortHead(root: string): string | null {
  if (!existsSync(join(root, ".git"))) return null;
  const proc = spawnSync("git", ["-C", root, "rev-parse", "--short", "HEAD"], {
    encoding: "utf-8",
  });
  return proc.status === 0 ? proc.stdout.trim() : null;
}

export function buildPortfolioDigest(input: PortfolioDigestInput): PortfolioDigestV0 {
  const verify = input.verify ?? {};
  return {
    object: "AgentsForOllamaPortfolioDigestV0",
    authority_status: "projection_not_truth",
    repo_root: input.root,
    git_head: gitShortHead(input.root),
    verify: {
      quality_gate: verify.quality_gate ?? "unknown",
      unit_tests: verify.unit_tests ?? "unknown",
      python_agents_smoke: verify.python_agents_smoke ?? "skipped",
      ts_governance: verify.ts_governance ?? "unknown",
    },
    bridge_objects: ["cas_return_packet_v0_1", "python_agents_sdk_cas_return_v0"],
    critical_path: "sigmem0_s3_to_mac_m4_1",
    posture: "wired_read_only",
  };
}
