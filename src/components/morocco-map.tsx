"use client";

import React, { useState, useCallback, useMemo, useEffect } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { GEO_REGIONS, type GeoRegion } from "@/lib/morocco-geo";

// ── Types ──────────────────────────────────────────────────────────────────
interface MoroccoMapProps {
  selectedRegion: string | null;
  onRegionClick: (region: string | null) => void;
  colorScale: (value: number, min: number, max: number) => string;
  regionValues: Record<string, number>;
  unit?: string;
}

// ── Projection helpers ─────────────────────────────────────────────────────
interface ProjectedRegion {
  name: string;
  population: number;
  pathD: string;
  centroidX: number;
  centroidY: number;
}

function projectRegions(padding = 0.05): {
  regions: ProjectedRegion[];
  viewBox: string;
  width: number;
  height: number;
} {
  // Find bounding box of all points
  let minLon = Infinity, maxLon = -Infinity, minLat = Infinity, maxLat = -Infinity;
  for (const r of GEO_REGIONS) {
    for (const [lon, lat] of r.points) {
      if (lon < minLon) minLon = lon;
      if (lon > maxLon) maxLon = lon;
      if (lat < minLat) minLat = lat;
      if (lat > maxLat) maxLat = lat;
    }
  }

  const lonRange = maxLon - minLon;
  const latRange = maxLat - minLat;
  const padLon = lonRange * padding;
  const padLat = latRange * padding;
  minLon -= padLon; maxLon += padLon;
  minLat -= padLat; maxLat += padLat;

  const adjustedLonRange = maxLon - minLon;
  const adjustedLatRange = maxLat - minLat;

  // Target SVG size: 400 x 500 (portrait for Morocco)
  const svgW = 400;
  const svgH = 500;

  // Scale to fit, maintaining aspect ratio
  const scaleX = svgW / adjustedLonRange;
  const scaleY = svgH / adjustedLatRange;
  const scale = Math.min(scaleX, scaleY);

  // Center the map
  const mapW = adjustedLonRange * scale;
  const mapH = adjustedLatRange * scale;
  const offsetX = (svgW - mapW) / 2;
  const offsetY = (svgH - mapH) / 2;

  const project = (lon: number, lat: number): [number, number] => {
    const x = offsetX + (lon - minLon) * scale;
    const y = offsetY + (maxLat - lat) * scale; // flip Y
    return [x, y];
  };

  const regions: ProjectedRegion[] = GEO_REGIONS.map((r) => {
    let sumX = 0, sumY = 0;
    const parts: string[] = [];

    for (let i = 0; i < r.points.length; i++) {
      const [lon, lat] = r.points[i];
      const [x, y] = project(lon, lat);
      sumX += x;
      sumY += y;
      if (i === 0) {
        parts.push(`M ${x.toFixed(1)},${y.toFixed(1)}`);
      } else {
        parts.push(`L ${x.toFixed(1)},${y.toFixed(1)}`);
      }
    }
    parts.push("Z");

    const n = r.points.length;
    return {
      name: r.name,
      population: r.population,
      pathD: parts.join(" "),
      centroidX: sumX / n,
      centroidY: sumY / n,
    };
  });

  return {
    regions,
    viewBox: `0 0 ${svgW} ${svgH}`,
    width: svgW,
    height: svgH,
  };
}

// Pre-compute projection (constant for the GeoJSON)
const MAP_DATA = projectRegions(0.04);

// ── Pulsing animation keyframes ────────────────────────────────────────────
const PULSE_STYLE_ID = "morocco-map-pulse-style";

function injectPulseStyle() {
  if (typeof document === "undefined") return;
  if (document.getElementById(PULSE_STYLE_ID)) return;
  const style = document.createElement("style");
  style.id = PULSE_STYLE_ID;
  style.textContent = `
    @keyframes morocco-pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.55; }
    }
    .region-pulse-path {
      animation: morocco-pulse 1.8s ease-in-out infinite;
    }
  `;
  document.head.appendChild(style);
}

// ── Component ──────────────────────────────────────────────────────────────
export default function MoroccoMap({
  selectedRegion,
  onRegionClick,
  colorScale,
  regionValues,
  unit = "",
}: MoroccoMapProps) {
  const [hoveredRegion, setHoveredRegion] = useState<string | null>(null);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });

  useEffect(() => {
    injectPulseStyle();
  }, []);

  const { regions, viewBox } = MAP_DATA;

  const { min, max } = useMemo(() => {
    const vals = Object.values(regionValues);
    if (vals.length === 0) return { min: 0, max: 1 };
    return { min: Math.min(...vals), max: Math.max(...vals) };
  }, [regionValues]);

  const handleMouseEnter = useCallback(
    (e: React.MouseEvent<SVGPathElement>, name: string) => {
      setHoveredRegion(name);
      const svg = e.currentTarget.closest("svg");
      if (svg) {
        const rect = svg.getBoundingClientRect();
        setTooltipPos({
          x: e.clientX - rect.left + 15,
          y: e.clientY - rect.top - 10,
        });
      }
    },
    []
  );

  const handleMouseMove = useCallback(
    (e: React.MouseEvent<SVGPathElement>) => {
      const svg = e.currentTarget.closest("svg");
      if (svg) {
        const rect = svg.getBoundingClientRect();
        setTooltipPos({
          x: e.clientX - rect.left + 15,
          y: e.clientY - rect.top - 10,
        });
      }
    },
    []
  );

  const handleRegionClick = useCallback(
    (name: string) => {
      onRegionClick(selectedRegion === name ? null : name);
    },
    [selectedRegion, onRegionClick]
  );

  const legendStops = useMemo(() => {
    if (min === max) return [colorScale(min, min, max)];
    return Array.from({ length: 5 }, (_, i) =>
      colorScale(min + ((max - min) * i) / 4, min, max)
    );
  }, [colorScale, min, max]);

  const formatValue = (val: number) => val.toLocaleString("fr-FR");

  // Abbreviated names for labels
  const abbrName = (name: string) => {
    const map: Record<string, string> = {
      "Tanger-Tétouan-Al Hoceima": "Tanger",
      "Rabat-Salé-Kénitra": "Rabat",
      "Fès-Meknès": "Fès-Meknès",
      "Béni Mellal-Khénifra": "B. Mellal",
      "Casablanca-Settat": "Casablanca",
      "Marrakech-Safi": "Marrakech",
      "Drâa-Tafilalet": "Drâa-Taf."
    };
    return map[name] || name;
  };

  return (
    <Card className="w-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-base">Carte Régionale du Maroc</CardTitle>
        <CardDescription className="text-xs">
          Coordonnées géographiques réelles — Découpage 12 régions (2015)
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Map container */}
        <div className="relative mx-auto w-full max-w-md" style={{ aspectRatio: "4/5" }}>
          <svg
            viewBox={viewBox}
            className="h-full w-full"
            xmlns="http://www.w3.org/2000/svg"
            style={{ filter: "drop-shadow(0 2px 8px rgba(0,0,0,0.08))" }}
          >
            {/* Light background */}
            <rect width="100%" height="100%" fill="#f8fafc" rx="4" />

            {/* Ocean/water areas hint */}
            <rect width="100%" height="100%" fill="#eef5ff" rx="4" opacity="0.5" />

            <g>
              {regions.map((region) => {
                const value = regionValues[region.name];
                const isHovered = hoveredRegion === region.name;
                const isSelected = selectedRegion === region.name;
                const fillColor = value !== undefined
                  ? colorScale(value, min, max)
                  : "#e2e8f0";

                return (
                  <g key={region.name}>
                    {/* Region path */}
                    <path
                      d={region.pathD}
                      fill={fillColor}
                      stroke={isSelected ? "#ffffff" : "#94a3b8"}
                      strokeWidth={isSelected ? 2.5 : 0.8}
                      strokeLinejoin="round"
                      className="cursor-pointer transition-all duration-150"
                      style={{
                        filter: isHovered
                          ? "brightness(1.12) saturate(1.2)"
                          : "none",
                        transform: isHovered
                          ? "translate(0, -1px)"
                          : "translate(0, 0)",
                      }}
                      onMouseEnter={(e) => handleMouseEnter(e, region.name)}
                      onMouseMove={handleMouseMove}
                      onMouseLeave={() => setHoveredRegion(null)}
                      onClick={() => handleRegionClick(region.name)}
                    />
                    {/* Selected region pulsing border */}
                    {isSelected && (
                      <path
                        d={region.pathD}
                        fill="none"
                        stroke="hsl(24, 85%, 53%)"
                        strokeWidth={3}
                        strokeLinejoin="round"
                        className="region-pulse-path pointer-events-none"
                      />
                    )}
                    {/* Region label */}
                    <text
                      x={region.centroidX}
                      y={region.centroidY}
                      textAnchor="middle"
                      dominantBaseline="central"
                      className="pointer-events-none select-none"
                      style={{
                        fontSize: region.name.includes("Drâa") || region.name.includes("Guelmim") || region.name.includes("Dakhla") || region.name.includes("Laâyoune")
                          ? "7px"
                          : "8px",
                        fontWeight: 600,
                        fill: isHovered || isSelected ? "#ffffff" : "#1e293b",
                        paintOrder: "stroke",
                        stroke: isHovered || isSelected
                          ? "rgba(0,0,0,0.6)"
                          : "rgba(255,255,255,0.85)",
                        strokeWidth: "2.5px",
                        strokeLinecap: "round",
                        strokeLinejoin: "round",
                        transition: "fill 150ms, stroke 150ms",
                      }}
                    >
                      {abbrName(region.name)}
                    </text>
                  </g>
                );
              })}
            </g>
          </svg>

          {/* Tooltip */}
          {hoveredRegion && (
            <div
              className="pointer-events-none absolute z-50 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm shadow-lg"
              style={{
                left: `${tooltipPos.x}px`,
                top: `${tooltipPos.y}px`,
                transform: "translateY(-100%)",
              }}
            >
              <div
                className="absolute left-4 top-full h-0 w-0"
                style={{
                  borderLeft: "6px solid transparent",
                  borderRight: "6px solid transparent",
                  borderTop: "6px solid white",
                }}
              />
              <div className="font-semibold text-slate-900">{hoveredRegion}</div>
              {hoveredRegion in regionValues && (
                <div className="mt-0.5 text-slate-600">
                  {formatValue(regionValues[hoveredRegion])}
                  {unit ? ` ${unit}` : ""}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Legend */}
        <div className="mt-3 flex flex-col items-center gap-1">
          <div className="flex w-full max-w-xs items-center gap-2">
            <span className="text-[10px] text-muted-foreground whitespace-nowrap">
              {formatValue(min)}
            </span>
            <div
              className="h-2.5 flex-1 rounded-sm"
              style={{
                background: `linear-gradient(to right, ${legendStops.join(", ")})`,
              }}
            />
            <span className="text-[10px] text-muted-foreground whitespace-nowrap">
              {formatValue(max)}
            </span>
          </div>
          {unit && (
            <span className="text-[10px] text-muted-foreground">{unit}</span>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
