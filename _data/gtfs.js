import { readFileSync } from "node:fs";
import { unzipSync, strFromU8 } from "fflate";
import Papa from "papaparse";

const DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"];
const DAY_NAMES = ["Mondays", "Tuesdays", "Wednesdays", "Thursdays", "Fridays", "Saturdays", "Sundays"];

function readFeed(path) {
  const files = unzipSync(readFileSync(path));
  const tables = {};
  for (const [name, bytes] of Object.entries(files)) {
    tables[name.replace(/\.txt$/, "")] = Papa.parse(strFromU8(bytes).replace(/^﻿/, ""), {
      header: true,
      skipEmptyLines: true,
    }).data;
  }
  return tables;
}

function groupBy(rows, key) {
  const map = new Map();
  for (const row of rows) {
    if (!map.has(row[key])) map.set(row[key], []);
    map.get(row[key]).push(row);
  }
  return map;
}

// "13:05:00" -> "1:05 PM"
function formatTime(time) {
  const [h, m] = time.split(":").map(Number);
  const suffix = h % 24 >= 12 ? "PM" : "AM";
  return `${((h + 11) % 12) + 1}:${String(m).padStart(2, "0")} ${suffix}`;
}

// "20270101" -> Date
function parseDate(date) {
  return new Date(Date.UTC(+date.slice(0, 4), +date.slice(4, 6) - 1, +date.slice(6, 8)));
}

function formatDate(date) {
  return parseDate(date).toLocaleDateString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
    timeZone: "UTC",
  });
}

// Drops shape points closer than ~40 m to the previous kept point, always keeping the last one
function thin(coords, minDeg = 0.0004) {
  const kept = [coords[0]];
  for (const c of coords.slice(1, -1)) {
    const last = kept.at(-1);
    if (Math.hypot(c[0] - last[0], c[1] - last[1]) >= minDeg) kept.push(c);
  }
  if (coords.length > 1) kept.push(coords.at(-1));
  return kept;
}

function townOf(stopName) {
  return stopName.split(" (")[0];
}

function describeService(calendar, dates) {
  if (!calendar) {
    return dates.length ? "Select dates" : "";
  }
  const days = DAYS.map((d) => calendar[d] === "1");
  const count = days.filter(Boolean).length;
  if (count === 7) return "7 days a week";
  if (count === 5 && days.slice(0, 5).every(Boolean)) return "Monday to Friday";
  if (count === 1) return DAY_NAMES[days.indexOf(true)];
  return DAY_NAMES.filter((_, i) => days[i]).join(", ");
}

export default function () {
  const feed = readFeed("west_gtfs.zip");
  const today = new Date().toISOString().slice(0, 10).replaceAll("-", "");

  const stops = new Map(feed.stops.map((s) => [s.stop_id, s]));
  const calendars = new Map(feed.calendar.map((c) => [c.service_id, c]));
  const calendarDates = groupBy(feed.calendar_dates ?? [], "service_id");
  const stopTimes = groupBy(feed.stop_times, "trip_id");
  const tripsByRoute = groupBy(feed.trips, "route_id");
  const shapes = groupBy(feed.shapes ?? [], "shape_id");
  const stopArea = new Map((feed.stop_areas ?? []).map((s) => [s.stop_id, s.area_id]));
  const routeNetwork = new Map((feed.route_networks ?? []).map((r) => [r.route_id, r.network_id]));
  const products = new Map((feed.fare_products ?? []).map((p) => [p.fare_product_id, p]));

  // Fare periods come from timeframes, ordered by the start of their service calendar
  const periods = (feed.timeframes ?? [])
    .map((t) => {
      const cal = calendars.get(t.service_id);
      return { id: t.timeframe_group_id, start: cal.start_date, end: cal.end_date };
    })
    .sort((a, b) => a.start.localeCompare(b.start))
    .map((p, i, all) => ({
      ...p,
      label: i === 0 ? `Until ${formatDate(p.end)}` : `From ${formatDate(p.start)}`,
      kind: i === 0 ? "until" : "from",
    }));

  // Fare amounts per network, origin area and period, split into one-way and round trip
  function faresFor(networkId, areaId) {
    const result = {};
    for (const rule of feed.fare_leg_rules ?? []) {
      if (rule.network_id !== networkId || (rule.from_area_id || "") !== (areaId || "")) continue;
      const product = products.get(rule.fare_product_id);
      const kind = rule.leg_group_id.endsWith("_RT") ? "roundTrip" : "oneWay";
      result[rule.from_timeframe_group_id] ??= {};
      result[rule.from_timeframe_group_id][kind] = `$${Number(product.amount).toFixed(0)}`;
    }
    return result;
  }

  const routes = feed.routes.map((route) => {
    const trips = (tripsByRoute.get(route.route_id) ?? []).map((trip) => ({
      ...trip,
      stopTimes: (stopTimes.get(trip.trip_id) ?? []).sort((a, b) => a.stop_sequence - b.stop_sequence),
    }));
    // The trip listed first in trips.txt sets the row order of the timetable
    const [first, second] = trips;
    const lastTown = (trip) => townOf(stops.get(trip.stopTimes.at(-1).stop_id).stop_name);
    const networkId = routeNetwork.get(route.route_id);
    const timeAt = (st) =>
      st.arrival_time === st.departure_time
        ? formatTime(st.departure_time)
        : `${formatTime(st.arrival_time)} / ${formatTime(st.departure_time)}`;

    const rows = first.stopTimes.map((st) => {
      const stop = stops.get(st.stop_id);
      const back = second?.stopTimes.find((o) => o.stop_id === st.stop_id);
      const area = stopArea.get(st.stop_id);
      const fares = area ? faresFor(networkId, area) : {};
      return {
        stopId: st.stop_id,
        town: townOf(stop.stop_name),
        location: stop.stop_desc,
        flag: st.pickup_type === "3",
        out: timeAt(st),
        back: back ? timeAt(back) : "",
        fares: Object.keys(fares).length ? fares : null,
      };
    });

    const serviceId = first.service_id;
    const dates = (calendarDates.get(serviceId) ?? [])
      .filter((d) => d.exception_type === "1")
      .map((d) => d.date)
      .sort();
    const routeFares = faresFor(networkId, "");

    return {
      id: route.route_id,
      name: route.route_long_name,
      description: route.route_desc,
      color: `#${route.route_color || "B00000"}`,
      textColor: `#${route.route_text_color || "FFFFFF"}`,
      service: describeService(calendars.get(serviceId), dates),
      serviceEnds: calendars.get(serviceId) ? formatDate(calendars.get(serviceId).end_date) : "",
      serviceStartDate: calendars.get(serviceId)?.start_date ?? "",
      serviceEndDate: calendars.get(serviceId)?.end_date ?? "",
      upcomingDateIds: dates.filter((d) => d >= today),
      upcomingDates: dates
        .filter((d) => d >= today)
        .map((d) => ({ iso: `${d.slice(0, 4)}-${d.slice(4, 6)}-${d.slice(6, 8)}`, label: formatDate(d) })),
      outLabel: `To ${lastTown(first)}`,
      backLabel: second ? `To ${lastTown(second)}` : "",
      outTown: lastTown(first),
      backTown: second ? lastTown(second) : "",
      hasRowFares: rows.some((r) => r.fares),
      fares: Object.keys(routeFares).length ? routeFares : null,
      rows,
      shapeIds: [...new Set(trips.map((t) => t.shape_id).filter(Boolean))],
      trips,
    };
  });

  // GeoJSON for the map: one line per shape, one point per stop with the routes and times serving it
  const features = [];
  for (const route of routes) {
    for (const shapeId of route.shapeIds) {
      const points = (shapes.get(shapeId) ?? []).sort((a, b) => a.shape_pt_sequence - b.shape_pt_sequence);
      if (!points.length) continue;
      features.push({
        type: "Feature",
        properties: { kind: "route", route: route.id, name: route.name, color: route.color, [`on_${route.id}`]: true },
        geometry: {
          type: "LineString",
          coordinates: thin(points.map((p) => [+(+p.shape_pt_lon).toFixed(5), +(+p.shape_pt_lat).toFixed(5)])),
        },
      });
    }
  }
  const stopServices = new Map();
  for (const route of routes) {
    for (const row of route.rows) {
      if (!stopServices.has(row.stopId)) stopServices.set(row.stopId, []);
      stopServices.get(row.stopId).push({
        route: route.id,
        name: route.name,
        color: route.color,
        times: [row.out && `${route.outLabel}: ${row.out}`, row.back && `${route.backLabel}: ${row.back}`].filter(Boolean),
        flag: row.flag,
      });
    }
  }
  for (const [stopId, services] of stopServices) {
    const stop = stops.get(stopId);
    features.push({
      type: "Feature",
      properties: {
        kind: "stop",
        id: stopId,
        name: stop.stop_name,
        location: stop.stop_desc,
        color: services[0].color,
        services,
        // Flat flags so map filters can match routes without array properties
        ...Object.fromEntries(services.map((s) => [`on_${s.route}`, true])),
      },
      geometry: { type: "Point", coordinates: [+stop.stop_lon, +stop.stop_lat] },
    });
  }

  return {
    agency: feed.agency[0],
    feedInfo: feed.feed_info?.[0],
    periods,
    currentPeriods: periods.filter((p) => p.end >= today),
    today,
    routes: routes.map(({ trips, shapeIds, ...r }) => r),
    geojson: { type: "FeatureCollection", features },
  };
}
