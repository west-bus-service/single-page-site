export const data = { permalink: "/newhomepage/network.geojson", eleventyExcludeFromCollections: true };

export function render({ gtfs }) {
  return JSON.stringify(gtfs.geojson);
}
