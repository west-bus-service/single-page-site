// Prints the built brochure pages in _site/brochure to PDFs at the site root using headless Chrome
import { execFileSync } from "node:child_process";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";
import puppeteer from "puppeteer-core";

const pages = { en: "brochure.pdf", es: "brochure-es.pdf" };
const candidates = [process.env.CHROME_PATH, "google-chrome", "google-chrome-stable", "chromium", "chromium-browser"];

function findChrome() {
  for (const bin of candidates.filter(Boolean)) {
    try {
      execFileSync(bin, ["--version"], { stdio: "ignore" });
      return execFileSync("which", [bin]).toString().trim() || bin;
    } catch {}
  }
  throw new Error("Chrome not found. Set CHROME_PATH to a Chrome or Chromium binary.");
}

const browser = await puppeteer.launch({
  executablePath: findChrome(),
  // Software WebGL so the maps render without a GPU
  args: ["--no-sandbox", "--allow-file-access-from-files", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"],
});
try {
  for (const [lang, pdf] of Object.entries(pages)) {
    const page = await browser.newPage();
    page.on("pageerror", (err) => console.error(`${lang}: ${err.message}`));
    await page.setViewport({ width: 1056, height: 816 });
    await page.goto(pathToFileURL(resolve(`_site/brochure/${lang}.html`)).href, { waitUntil: "networkidle0" });
    await page.waitForFunction(() => window.mapsReady, { timeout: 60000 });
    await page.evaluate(() => window.mapsReady);
    await page.pdf({ path: resolve("_site", pdf), preferCSSPageSize: true, printBackground: true });
    await page.close();
    console.log(`Wrote _site/${pdf}`);
  }
} finally {
  await browser.close();
}
