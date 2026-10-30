// Per-route maps drawn from the GTFS feed (network.geojson is generated at build time)
(function () {
  const containers = [...document.querySelectorAll(".route-map[data-route]")];
  if (!containers.length || !window.maplibregl) return;

  const network = fetch("network.geojson").then((r) => r.json());

  function popupContent(stop) {
    const root = document.createElement("div");
    root.className = "popup";
    const title = document.createElement("h4");
    title.textContent = stop.name;
    const where = document.createElement("p");
    where.className = "where";
    where.textContent = stop.location;
    root.append(title, where);
    for (const svc of stop.services) {
      const block = document.createElement("div");
      block.className = "svc";
      block.style.setProperty("--route", svc.color);
      const name = document.createElement("strong");
      name.textContent = svc.name + (svc.flag ? " (flag stop)" : "");
      block.append(name);
      for (const t of svc.times) {
        const line = document.createElement("div");
        line.textContent = t;
        block.append(line);
      }
      root.append(block);
    }
    return root;
  }

  function initMap(container) {
    const route = container.dataset.route;
    const color = getComputedStyle(container).getPropertyValue("--route").trim();
    const map = new maplibregl.Map({
      container,
      style: "https://tiles.openfreemap.org/styles/positron",
      center: [-68.0, 44.8],
      zoom: 7.5,
      cooperativeGestures: true,
      attributionControl: { compact: true },
    });
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
    map.addControl(new maplibregl.FullscreenControl(), "top-right");

    map.on("load", async () => {
      const all = await network;
      // Only this route's line and the stops it serves
      const features = all.features.filter((f) => f.properties[`on_${route}`]);
      const stopsById = new Map();
      for (const f of features) {
        if (f.properties.kind === "stop") stopsById.set(f.properties.id, f.properties);
      }
      map.addSource("network", { type: "geojson", data: { type: "FeatureCollection", features } });

      const isRoute = ["==", ["get", "kind"], "route"];
      const isStop = ["==", ["get", "kind"], "stop"];
      map.addLayer({
        id: "routes-casing",
        type: "line",
        source: "network",
        filter: isRoute,
        layout: { "line-join": "round", "line-cap": "round" },
        paint: { "line-color": "#ffffff", "line-width": ["interpolate", ["linear"], ["zoom"], 7, 5, 12, 9] },
      });
      map.addLayer({
        id: "routes",
        type: "line",
        source: "network",
        filter: isRoute,
        layout: { "line-join": "round", "line-cap": "round" },
        paint: { "line-color": ["get", "color"], "line-width": ["interpolate", ["linear"], ["zoom"], 7, 3, 12, 6] },
      });
      map.addLayer({
        id: "stops",
        type: "circle",
        source: "network",
        filter: isStop,
        paint: {
          "circle-radius": ["interpolate", ["linear"], ["zoom"], 7, 4.5, 12, 8],
          "circle-color": "#ffffff",
          "circle-stroke-color": color,
          "circle-stroke-width": 3,
        },
      });
      map.addLayer({
        id: "stop-labels",
        type: "symbol",
        source: "network",
        filter: isStop,
        minzoom: 8,
        layout: {
          "text-field": ["get", "name"],
          "text-font": ["Noto Sans Bold"],
          "text-size": 13,
          "text-offset": [0, 1.1],
          "text-anchor": "top",
          "text-optional": true,
        },
        paint: { "text-color": "#14285f", "text-halo-color": "#ffffff", "text-halo-width": 2 },
      });

      const bounds = new maplibregl.LngLatBounds();
      for (const f of features) {
        if (f.geometry.type === "Point") bounds.extend(f.geometry.coordinates);
        else f.geometry.coordinates.forEach((c) => bounds.extend(c));
      }
      if (!bounds.isEmpty()) map.fitBounds(bounds, { padding: 30, duration: 0 });

      map.on("click", "stops", (e) => {
        const stop = stopsById.get(e.features[0].properties.id);
        new maplibregl.Popup({ maxWidth: "300px" })
          .setLngLat(e.features[0].geometry.coordinates)
          .setDOMContent(popupContent(stop))
          .addTo(map);
      });
      map.on("mouseenter", "stops", () => (map.getCanvas().style.cursor = "pointer"));
      map.on("mouseleave", "stops", () => (map.getCanvas().style.cursor = ""));
    });
  }

  // Create each map when it nears the viewport
  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        observer.unobserve(entry.target);
        initMap(entry.target);
      }
    },
    { rootMargin: "400px 0px" },
  );
  containers.forEach((c) => observer.observe(c));
})();
