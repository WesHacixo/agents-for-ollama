import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const SRC_DIR = dirname(fileURLToPath(import.meta.url));

export const PACKAGE_ROOT = resolve(SRC_DIR, "..");
export const REPO_ROOT = resolve(PACKAGE_ROOT, "../..");

export const MANIFEST_REL = "packages/detached_membrane_sdk/spec/detached-membrane-manifest.v1.json";
export const POLICY_SOURCE_REL = "packages/detached_membrane_sdk/policy/policy_source.json";
export const POLICY_GENERATED_REL = "packages/detached_membrane_sdk/policy/generated";
export const ZTNA_POLICY_REL = "packages/detached_membrane_sdk/policy/local_ztna_policy_v0.json";
