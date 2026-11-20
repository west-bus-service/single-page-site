export const data = { permalink: "/network.geojson", eleventyExcludeFromCollections: true };

export function render({ gtfs }) {
  return JSON.stringify(gtfs.geojson);
}
