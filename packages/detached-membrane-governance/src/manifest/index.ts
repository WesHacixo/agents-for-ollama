import { createHash } from "node:crypto";
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";

export type ManifestArtifact = { path: string; role?: string };
export type ManifestDocument = {
  declared_checksum: string;
  artifacts: ManifestArtifact[];
  invariants?: Array<{ id: string; text: string }>;
};

export type ArtifactRecord = { path: string; sha256: string };

export function sha256File(filePath: string): string {
  return createHash("sha256").update(readFileSync(filePath)).digest("hex");
}

export function artifactChecksumRecords(
  root: string,
  artifacts: ManifestArtifact[],
): ArtifactRecord[] {
  const records: ArtifactRecord[] = [];
  for (const entry of artifacts) {
    const filePath = join(root, entry.path);
    if (!existsSync(filePath)) {
      throw new Error(`missing manifest artifact: ${entry.path}`);
    }
    records.push({ path: entry.path, sha256: sha256File(filePath) });
  }
  return records.sort((a, b) => a.path.localeCompare(b.path));
}

export function computeArtifactsChecksum(records: ArtifactRecord[]): string {
  const canonical = JSON.stringify(records);
  return createHash("sha256").update(canonical).digest("hex");
}

export function loadManifest(manifestPath: string): ManifestDocument {
  return JSON.parse(readFileSync(manifestPath, "utf-8")) as ManifestDocument;
}

export function verifyManifest(
  manifestPath: string,
  root: string,
): { ok: boolean; reasons: string[] } {
  const reasons: string[] = [];
  const manifest = loadManifest(manifestPath);
  const artifacts = manifest.artifacts;

  if (!Array.isArray(artifacts) || artifacts.length === 0) {
    return { ok: false, reasons: ["manifest artifacts list is missing or empty"] };
  }

  const declared = manifest.declared_checksum;
  if (!declared) {
    return { ok: false, reasons: ["manifest declared_checksum is missing"] };
  }

  let records: ArtifactRecord[];
  try {
    records = artifactChecksumRecords(root, artifacts);
  } catch (err) {
    return { ok: false, reasons: [err instanceof Error ? err.message : String(err)] };
  }

  const actual = computeArtifactsChecksum(records);
  if (actual !== declared) {
    reasons.push(
      `checksum mismatch: declared=${declared} actual=${actual} ` +
        "(run membrane:refresh-manifest after intentional edits)",
    );
  } else {
    reasons.push(`checksum match: ${actual}`);
  }

  for (const invariant of manifest.invariants ?? []) {
    const invId = invariant.id ?? "unknown";
    if (!invariant.text) {
      reasons.push(`invariant ${invId}: missing text`);
    } else {
      reasons.push(`invariant ${invId}: declared`);
    }
  }

  return { ok: actual === declared, reasons };
}

export function refreshDeclaredChecksum(manifestPath: string, root: string): string {
  const raw = readFileSync(manifestPath, "utf-8");
  const manifest = JSON.parse(raw) as ManifestDocument;
  const records = artifactChecksumRecords(root, manifest.artifacts);
  const checksum = computeArtifactsChecksum(records);
  manifest.declared_checksum = checksum;
  writeFileSync(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`, "utf-8");
  return checksum;
}
