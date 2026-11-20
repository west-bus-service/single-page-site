// Static per-route maps for the printed brochure; window.mapsReady resolves once every map has finished rendering
(function () {
  const network = JSON.parse(document.getElementById("network").textContent);
  const containers = [...document.querySelectorAll(".route-map[data-route]")];

  // Rasterizes the flag SVG at 4x to match the map pixelRatio
  const flagImage = (async () => {
    const img = new Image();
    img.src = "../flag.svg";
    await img.decode();
    const canvas = document.createElement("canvas");
    canvas.width = 80;
    canvas.height = 64;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    return ctx.getImageData(0, 0, canvas.width, canvas.height);
  })();

  function initMap(container) {
    const route = container.dataset.route;
    const color = getComputedStyle(container).getPropertyValue("--route").trim();
    // Only this route's line and the stops it serves, with one label per town
    const towns = new Set();
    const features = network.features
      .filter((f) => f.properties[`on_${route}`])
      .map((f) => {
        const town = f.properties.name?.split(" (")[0];
        const label = town && !towns.has(town) ? town : "";
        towns.add(town);
        return { ...f, properties: { ...f.properties, town: label } };
      });
    const bounds = new maplibregl.LngLatBounds();
    for (const f of features) {
      if (f.geometry.type === "Point") bounds.extend(f.geometry.coordinates);
      else f.geometry.coordinates.forEach((c) => bounds.extend(c));
    }

    const map = new maplibregl.Map({
      container,
      style: "https://tiles.openfreemap.org/styles/positron",
      bounds,
      fitBoundsOptions: { padding: { top: 12, bottom: 12, left: 48, right: 48 } },
      interactive: false,
      attributionControl: false,
      fadeDuration: 0,
      pixelRatio: 4,
      canvasContextAttributes: { preserveDrawingBuffer: true },
    });

    return new Promise((resolve) => {
      map.on("load", async () => {
        // Drops the basemap's own labels so only the route's stops are named
        for (const layer of map.getStyle().layers) {
          if (layer.type === "symbol") map.removeLayer(layer.id);
        }
        map.addImage("flag", await flagImage, { pixelRatio: 4 });
        map.addSource("network", { type: "geojson", data: { type: "FeatureCollection", features } });
        const isRoute = ["==", ["get", "kind"], "route"];
        const isStop = ["==", ["get", "kind"], "stop"];
        const isFlag = ["to-boolean", ["get", `flag_${route}`]];
        map.addLayer({
          id: "routes-casing",
          type: "line",
          source: "network",
          filter: isRoute,
          layout: { "line-join": "round", "line-cap": "round" },
          paint: { "line-color": "#ffffff", "line-width": 4 },
        });
        map.addLayer({
          id: "routes",
          type: "line",
          source: "network",
          filter: isRoute,
          layout: { "line-join": "round", "line-cap": "round" },
          paint: { "line-color": ["get", "color"], "line-width": 2.2 },
        });
        map.addLayer({
          id: "stops",
          type: "circle",
          source: "network",
          filter: ["all", isStop, ["!", isFlag]],
          paint: { "circle-radius": 2.4, "circle-color": "#ffffff", "circle-stroke-color": color, "circle-stroke-width": 1.4 },
        });
        // Flag stops: icon only, pole base sits on the stop
        map.addLayer({
          id: "flag-stops",
          type: "symbol",
          source: "network",
          filter: ["all", isStop, isFlag],
          layout: {
            "icon-image": "flag",
            "icon-size": 0.5,
            "icon-anchor": "bottom-left",
            "icon-offset": [-4, 0],
            "icon-allow-overlap": true,
            "icon-ignore-placement": true,
          },
        });
        map.addLayer({
          id: "stop-labels",
          type: "symbol",
          source: "network",
          filter: ["all", isStop, ["!", isFlag]],
          layout: {
            "text-field": ["get", "town"],
            "text-font": ["Noto Sans Regular"],
            "text-size": 7,
            "text-variable-anchor": ["left", "right", "top", "bottom", "top-left", "top-right", "bottom-left", "bottom-right"],
            "text-radial-offset": 0.5,
            "text-justify": "auto",
            "text-padding": 0,
          },
          paint: { "text-color": "#1b1b1b", "text-halo-color": "#ffffff", "text-halo-width": 1.2 },
        });
        map.once("idle", resolve);
      });
      map.on("error", resolve);
    });
  }

  window.mapsReady = Promise.all(containers.map(initMap));
})();
