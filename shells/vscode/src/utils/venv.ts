import * as path from "path";

export function getCapExecutable(venvDir: string): string {
  return process.platform === "win32"
    ? path.join(venvDir, "Scripts", "cap.exe")
    : path.join(venvDir, "bin", "cap");
}

export function getVenvPython(venvDir: string): string {
  return process.platform === "win32"
    ? path.join(venvDir, "Scripts", "python.exe")
    : path.join(venvDir, "bin", "python");
}
