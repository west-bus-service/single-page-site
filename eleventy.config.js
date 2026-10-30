export default function (eleventyConfig) {
  for (const path of [
    "CNAME",
    "*.gif",
    "*.jpg",
    "*.jpeg",
    "*.JPG",
    "*.png",
    "favicon.ico",
    "favicon.svg",
    "newlogo.svg",
    "site.webmanifest",
    "*.pdf",
    "index_files",
    "route.geojson",
    "west_gtfs.zip",
    "newhomepage/style.css",
    "newhomepage/map.js",
    "brochure/brochure.css",
    "brochure/map.js",
  ]) {
    eleventyConfig.addPassthroughCopy(path);
  }
  eleventyConfig.addWatchTarget("cancellation_message.html");
  eleventyConfig.addWatchTarget("west_gtfs.zip");

  // "20270101" -> "January 1, 2027" in the given locale
  eleventyConfig.addFilter("gtfsDate", (date, locale = "en-US", month = "long") =>
    new Date(Date.UTC(+date.slice(0, 4), +date.slice(4, 6) - 1, +date.slice(6, 8))).toLocaleDateString(locale, {
      month,
      day: "numeric",
      year: "numeric",
      timeZone: "UTC",
    }),
  );
}
