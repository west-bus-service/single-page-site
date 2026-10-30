import { readFileSync } from "node:fs";

// Banner text shown at the top of the pages; empty file hides the banner
export default function () {
  return readFileSync("cancellation_message.html", "utf8").trim();
}
