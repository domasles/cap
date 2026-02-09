export function parseSemver(version: string): [number, number, number] {
  const parts = version.split(".").map(Number);
  return [parts[0] ?? 0, parts[1] ?? 0, parts[2] ?? 0];
}

export function isNewer(a: string, b: string): boolean {
  const av = parseSemver(a);
  const bv = parseSemver(b);

  for (let i = 0; i < 3; i++) {
    if (av[i] > bv[i]) return true;
    if (av[i] < bv[i]) return false;
  }

  return false;
}

export function maxVersion(versions: string[]): string | undefined {
  if (versions.length === 0) return undefined;
  return versions.reduce((max, v) => (isNewer(v, max) ? v : max));
}
