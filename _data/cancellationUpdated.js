import { execFileSync } from "node:child_process";
import { statSync } from "node:fs";

const FILE = "cancellation_message.html";

// Last commit date of the banner file, falling back to its mtime outside git
export default function () {
  let date;
  try {
    const iso = execFileSync("git", ["log", "-1", "--format=%cI", "--", FILE], { encoding: "utf8" }).trim();
    if (iso) date = new Date(iso);
  } catch {}
  date ??= statSync(FILE).mtime;
  return {
    iso: date.toISOString(),
    label: date.toLocaleDateString("en-US", { timeZone: "America/New_York", month: "short", day: "numeric", year: "numeric" }),
  };
}
