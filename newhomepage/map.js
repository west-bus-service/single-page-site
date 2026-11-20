// Per-route maps drawn from the GTFS feed (network.geojson is generated at build time)
(function () {
  const containers = [...document.querySelectorAll(".route-map[data-route]")];
  if (!containers.length || !window.maplibregl) return;

  const network = fetch("network.geojson").then((r) => r.json());

  // Rasterizes the flag SVG at 2x for map.addImage
  const flagImage = (async () => {
    const img = new Image();
    img.src = "../flag.svg";
    await img.decode();
    const canvas = document.createElement("canvas");
    canvas.width = 40;
    canvas.height = 32;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    return ctx.getImageData(0, 0, canvas.width, canvas.height);
  })();

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
      const [all, flag] = await Promise.all([network, flagImage]);
      // Drops the basemap's own labels so only the route's stops are named
      for (const layer of map.getStyle().layers) {
        if (layer.type === "symbol") map.removeLayer(layer.id);
      }
      map.addImage("flag", flag, { pixelRatio: 2 });

      // Only this route's line and the stops it serves
      const features = all.features.filter((f) => f.properties[`on_${route}`]);
      const stopsById = new Map();
      for (const f of features) {
        if (f.properties.kind === "stop") stopsById.set(f.properties.id, f.properties);
      }
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
        filter: ["all", isStop, ["!", isFlag]],
        paint: {
          "circle-radius": ["interpolate", ["linear"], ["zoom"], 7, 4.5, 12, 8],
          "circle-color": "#ffffff",
          "circle-stroke-color": color,
          "circle-stroke-width": 3,
        },
      });
      // Flag stops: icon only, pole base sits on the stop; placed before labels so labels avoid the icon
      map.addLayer({
        id: "flag-stops",
        type: "symbol",
        source: "network",
        filter: ["all", isStop, isFlag],
        layout: {
          "icon-image": "flag",
          "icon-anchor": "bottom-left",
          "icon-offset": [-4, 0],
          "icon-allow-overlap": true,
        },
      });
      map.addLayer({
        id: "stop-labels",
        type: "symbol",
        source: "network",
        filter: ["all", isStop, ["!", isFlag]],
        layout: {
          "text-field": ["get", "name"],
          "text-font": ["Noto Sans Bold"],
          "text-size": 13,
          "text-variable-anchor": ["top", "bottom", "left", "right", "top-left", "top-right", "bottom-left", "bottom-right"],
          "text-radial-offset": 0.8,
          "text-justify": "auto",
          "text-padding": 1,
        },
        paint: {
          "text-color": "#14285f",
          "text-halo-color": "#ffffff",
          "text-halo-width": 2,
        },
      });

      const bounds = new maplibregl.LngLatBounds();
      for (const f of features) {
        if (f.geometry.type === "Point") bounds.extend(f.geometry.coordinates);
        else f.geometry.coordinates.forEach((c) => bounds.extend(c));
      }
      if (!bounds.isEmpty()) map.fitBounds(bounds, { padding: 30, duration: 0 });

      const clickable = ["stops", "flag-stops"];
      map.on("click", clickable, (e) => {
        const stop = stopsById.get(e.features[0].properties.id);
        new maplibregl.Popup({ maxWidth: "300px" })
          .setLngLat(e.features[0].geometry.coordinates)
          .setDOMContent(popupContent(stop))
          .addTo(map);
      });
      map.on("mouseenter", clickable, () => (map.getCanvas().style.cursor = "pointer"));
      map.on("mouseleave", clickable, () => (map.getCanvas().style.cursor = ""));
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
