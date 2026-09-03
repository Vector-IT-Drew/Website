(function (global) {
    const COLORS = {
        land: "#24354c",
        landDark: "#1f3046",
        water: "#0d2847",
        waterDark: "#0a213a",
        road: "#46566b",
        roadMinor: "#34465b",
        roadStroke: "#1b2b40",
        gold: "#a88c60",
        goldBright: "#d59563",
        goldLight: "#f3d19c",
        label: "#a88c60",
        labelBright: "#d59563",
        labelMuted: "#7e806f",
        park: "#29423f",
        parkLabel: "#6b9a76",
        building: "#203148"
    };

    function escapeHTML(value) {
        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function showError(container, message) {
        let el = container.querySelector(".map-error");
        if (!el) {
            el = document.createElement("div");
            el.className = "map-error";
            container.appendChild(el);
        }
        el.textContent = message;
        el.style.display = "block";
    }

    function vectorNYStyle(previous, next) {
        const style = JSON.parse(JSON.stringify(next));

        style.layers = style.layers.map((layer) => {
            const l = JSON.parse(JSON.stringify(layer));
            const id = (l.id || "").toLowerCase();
            const sourceLayer = (l["source-layer"] || "").toLowerCase();

            l.layout = l.layout || {};
            l.paint = l.paint || {};

            if (
                sourceLayer.includes("poi") ||
                sourceLayer.includes("aeroway") ||
                sourceLayer.includes("housenumber") ||
                sourceLayer.includes("airport") ||
                id.includes("poi") ||
                id.includes("aeroway") ||
                id.includes("housenumber")
            ) {
                l.layout.visibility = "none";
                return l;
            }

            if (l.type === "hillshade" || id.includes("hillshade") || sourceLayer.includes("hillshade")) {
                l.layout.visibility = "none";
                return l;
            }

            if (
                sourceLayer.includes("boundary") ||
                sourceLayer.includes("admin") ||
                id.includes("boundary")
            ) {
                l.paint["line-color"] = COLORS.roadStroke;
                l.paint["line-opacity"] = 0.15;
            }

            if (l.type === "background") {
                l.paint["background-color"] = COLORS.land;
            }

            if (l.type === "fill") {
                delete l.paint["fill-pattern"];
                if (l.paint["fill-color"] === undefined) {
                    l.paint["fill-color"] = COLORS.land;
                }
                if (l.paint["fill-opacity"] === undefined) {
                    l.paint["fill-opacity"] = 1;
                }
            }

            if (l.type === "fill-extrusion" && l.paint["fill-extrusion-color"] === undefined) {
                l.paint["fill-extrusion-color"] = COLORS.land;
            }

            if (sourceLayer === "water" || sourceLayer.includes("water")) {
                if (l.type === "fill") {
                    l.paint["fill-color"] = COLORS.water;
                    l.paint["fill-opacity"] = 1;
                }
                if (l.type === "line") {
                    l.paint["line-color"] = COLORS.waterDark;
                }
                if (l.type === "symbol") {
                    l.paint["text-color"] = "#657487";
                    l.paint["text-halo-color"] = COLORS.water;
                    l.paint["text-halo-width"] = 1.5;
                }
            }

            if (
                sourceLayer.includes("park") ||
                sourceLayer.includes("landcover") ||
                sourceLayer.includes("landuse")
            ) {
                if (l.type === "fill") {
                    l.paint["fill-color"] = COLORS.land;
                    l.paint["fill-opacity"] = 0.78;
                }
                if (l.type === "line") {
                    l.paint["line-color"] = "#36544c";
                    l.paint["line-opacity"] = 0.6;
                }
                if (l.type === "symbol") {
                    l.paint["text-color"] = COLORS.parkLabel;
                    l.paint["text-halo-color"] = COLORS.land;
                    l.paint["text-halo-width"] = 1.2;
                }
            }

            if (sourceLayer === "building" || sourceLayer.includes("building")) {
                if (l.type === "fill-extrusion") {
                    l.layout.visibility = "none";
                }
                if (l.type === "fill") {
                    l.paint["fill-color"] = "#b7bec6";
                    l.paint["fill-opacity"] = 0.075;
                }
                if (l.type === "line") {
                    l.paint["line-color"] = "#aeb6c0";
                    l.paint["line-opacity"] = 0.10;
                }
            }

            if (
                sourceLayer === "transportation" ||
                sourceLayer === "transportation_name" ||
                sourceLayer.includes("road")
            ) {
                if (l.type === "line") {
                    if (id.includes("hatching")) {
                        l.layout.visibility = "none";
                        return l;
                    }

                    delete l.paint["line-dasharray"];
                    delete l.paint["line-pattern"];
                    delete l.paint["line-gradient"];

                    l.layout["line-cap"] = "round";
                    l.layout["line-join"] = "round";

                    l.paint["line-color"] = [
                        "match",
                        ["get", "class"],
                        "motorway", COLORS.gold,
                        "trunk", COLORS.gold,
                        "primary", COLORS.gold,
                        "secondary", COLORS.road,
                        "tertiary", COLORS.road,
                        COLORS.roadMinor
                    ];

                    l.paint["line-opacity"] = [
                        "match",
                        ["get", "class"],
                        "motorway", 0.95,
                        "trunk", 0.92,
                        "primary", 0.85,
                        "secondary", 0.68,
                        "tertiary", 0.55,
                        0.38
                    ];

                    if (l.paint["line-width"] !== undefined) {
                        l.paint["line-width"] = [
                            "interpolate",
                            ["linear"],
                            ["zoom"],
                            10, 0.6,
                            13, 1.0,
                            16, 1.7,
                            18, 2.4
                        ];
                    }

                    if (id.includes("casing") || id.includes("bridge")) {
                        l.paint["line-color"] = [
                            "match",
                            ["get", "class"],
                            "motorway", COLORS.gold,
                            "trunk", COLORS.gold,
                            "primary", COLORS.gold,
                            "secondary", COLORS.road,
                            "tertiary", COLORS.road,
                            COLORS.roadMinor
                        ];
                        l.paint["line-opacity"] = [
                            "match",
                            ["get", "class"],
                            "motorway", 0.95,
                            "trunk", 0.92,
                            "primary", 0.85,
                            "secondary", 0.68,
                            "tertiary", 0.55,
                            0.38
                        ];
                    }
                }

                if (l.type === "symbol") {
                    l.paint["text-color"] = COLORS.label;
                    l.paint["text-halo-color"] = COLORS.land;
                    l.paint["text-halo-width"] = 1.5;
                    l.paint["text-halo-blur"] = 0.2;
                    if (l.layout["icon-image"] !== undefined) {
                        l.layout["icon-image"] = "";
                    }
                }
            }

            if (sourceLayer === "place" || sourceLayer.includes("place")) {
                if (l.type === "symbol") {
                    l.paint["text-color"] = COLORS.label;
                    l.paint["text-halo-color"] = COLORS.land;
                    l.paint["text-halo-width"] = 2;
                    l.paint["text-halo-blur"] = 0.25;
                    if (l.layout["text-size"] !== undefined) {
                        l.layout["text-size"] = [
                            "interpolate",
                            ["linear"],
                            ["zoom"],
                            10, 10,
                            13, 12,
                            15, 14,
                            17, 16,
                            19, 18
                        ];
                    }
                }
            }

            if (
                sourceLayer.includes("transportation_name") &&
                (id.includes("rail") || id.includes("transit"))
            ) {
                l.layout.visibility = "none";
            }

            return l;
        });

        style.glyphs = style.glyphs || next.glyphs;
        return style;
    }

    function createPropertyMap(container, property) {
        if (!global.maplibregl) {
            showError(container, "MapLibre did not load. Check your internet connection.");
            return null;
        }

        const lat = Number(property.lat);
        const lng = Number(property.lng);
        if (!Number.isFinite(lat) || !Number.isFinite(lng) || (lat === 0 && lng === 0)) {
            showError(container, "Map location is not available for this listing.");
            return null;
        }

        const map = new global.maplibregl.Map({
            container: container,
            style: "https://tiles.openfreemap.org/styles/liberty",
            center: [lng, lat],
            zoom: property.zoom || 14.6,
            minZoom: 3,
            maxZoom: 20,
            attributionControl: true,
            pitchWithRotate: false,
            dragRotate: false,
            scrollZoom: false,
            cooperativeGestures: true
        });

        map.addControl(
            new global.maplibregl.NavigationControl({
                showCompass: false,
                showZoom: true,
                visualizePitch: false
            }),
            "top-right"
        );

        let styled = false;
        map.once("style.load", function () {
            if (!styled) {
                styled = true;
                map.setStyle("https://tiles.openfreemap.org/styles/liberty", {
                    diff: false,
                    transformStyle: vectorNYStyle
                });
            }
        });

        map.on("style.load", function () {
            if (map.getSource("property-point")) {
                return;
            }

            map.addSource("property-point", {
                type: "geojson",
                data: {
                    type: "Feature",
                    properties: {},
                    geometry: {
                        type: "Point",
                        coordinates: [lng, lat]
                    }
                }
            });

            map.addLayer({
                id: "property-halo",
                type: "circle",
                source: "property-point",
                paint: {
                    "circle-radius": 19,
                    "circle-color": COLORS.goldBright,
                    "circle-opacity": 0.14,
                    "circle-stroke-color": COLORS.goldBright,
                    "circle-stroke-width": 1,
                    "circle-stroke-opacity": 0.40
                }
            });

            const markerElement = document.createElement("div");
            markerElement.className = "property-marker";

            new global.maplibregl.Marker({
                element: markerElement,
                anchor: "center"
            })
                .setLngLat([lng, lat])
                .setPopup(
                    new global.maplibregl.Popup({
                        offset: 20,
                        closeButton: true
                    }).setHTML(`
                        <div class="property-popup">
                          <div class="eyebrow">Property</div>
                          <div class="address">${escapeHTML(property.address || "")}</div>
                          <div class="location">${escapeHTML(property.city || "")}</div>
                        </div>
                    `)
                )
                .addTo(map);
        });

        function fitMapToContainer() {
            map.resize();
        }

        map.on("load", fitMapToContainer);
        map.on("idle", function onIdle() {
            fitMapToContainer();
            map.off("idle", onIdle);
        });

        if (typeof ResizeObserver !== "undefined") {
            const observer = new ResizeObserver(fitMapToContainer);
            observer.observe(container);
        } else {
            global.addEventListener("resize", fitMapToContainer);
        }

        map.on("error", function (e) {
            console.warn("MapLibre:", e && e.error ? e.error.message : e);
        });

        return map;
    }

    global.VectorNYMap = {
        COLORS: COLORS,
        create: createPropertyMap
    };
})(window);
