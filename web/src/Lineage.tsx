import { useEffect, useMemo, useRef, useState } from "react";
import { ArrowUpRight, Maximize2, Minus, Plus, RotateCcw } from "lucide-react";
import type { Graph, GraphNode, Result } from "./types";
import { number } from "./components";
export default function Lineage({
  graph,
  root,
  result,
  onNode,
}: {
  graph: Graph;
  root: string;
  result: Result | null;
  onNode: (n: GraphNode) => void;
}) {
  const [zoom, setZoom] = useState(1);
  const container = useRef<HTMLDivElement>(null),
    [fit, setFit] = useState(1);
  const layout = useMemo(() => {
    const edges = graph.edges.filter((e) => e.kind === "INPUT_TO");
    const depth = new Map([[root, 0]]);
    for (let i = 0; i < 6; i++)
      for (const e of edges)
        if (depth.has(e.source) && !depth.has(e.target))
          depth.set(e.target, depth.get(e.source)! + 1);
    const nodes = graph.nodes.filter((n) => depth.has(n.id));
    const positions = new Map<string, { x: number; y: number }>();
    const groups = new Map<number, GraphNode[]>();
    for (const n of nodes) {
      const d = depth.get(n.id)!;
      groups.set(d, [...(groups.get(d) || []), n]);
    }
    for (const [d, items] of groups) {
      items.sort((a, b) => {
        const au = edges.some(
          (e) => e.target === a.id && e.evidence !== "confirmed",
        );
        const bu = edges.some(
          (e) => e.target === b.id && e.evidence !== "confirmed",
        );
        return Number(au) - Number(bu) || a.id.localeCompare(b.id);
      });
      items.forEach((n, i) =>
        positions.set(n.id, {
          x: 30 + d * 205,
          y:
            items.length === 1
              ? 142
              : items.length === 2
                ? 64 + i * 166
                : 36 + i * 128,
        }),
      );
    }
    return {
      nodes,
      edges: edges.filter((e) => depth.has(e.source) && depth.has(e.target)),
      positions,
      width: Math.max(850, groups.size * 205 + 30),
    };
  }, [graph, root]);
  useEffect(() => {
    if (!container.current) return;
    const observer = new ResizeObserver(([entry]) => {
      const width = entry.contentRect.width;
      setFit(width >= 600 ? Math.min(1, width / layout.width) : 1);
    });
    observer.observe(container.current);
    return () => observer.disconnect();
  }, [layout.width]);
  const active = new Set(result?.confirmed.flatMap((s) => s.path) || []);
  if (!layout.nodes.length)
    return (
      <section className="lineage-panel">
        <div className="empty-table">
          This lot is not in the graph. No lineage or affected stock was
          inferred.
        </div>
      </section>
    );
  return (
    <section className="lineage-panel" aria-label="Material lineage">
      <div className="panel-heading">
        <div>
          <h2>Follow the lot</h2>
          <p>Every transformation leaves a connection.</p>
        </div>
        <span className="quiet-label">{layout.edges.length} connections</span>
      </div>
      <div className="diagram-scroll" ref={container}>
        <div
          className="diagram"
          style={{ width: layout.width * zoom * fit, height: 410 * zoom * fit }}
        >
          <svg
            width={layout.width * zoom * fit}
            height={410 * zoom * fit}
            viewBox={`0 0 ${layout.width} 410`}
            role="group"
            aria-label="Material lineage. Select a lot below or use the shipment table for a text equivalent."
          >
            <defs>
              <pattern
                id="dots"
                width="18"
                height="18"
                patternUnits="userSpaceOnUse"
              >
                <circle cx="1" cy="1" r=".7" fill="var(--color-line)" />
              </pattern>
              <marker
                id="arrow"
                viewBox="0 0 10 10"
                refX="9"
                refY="5"
                markerWidth="5"
                markerHeight="5"
                orient="auto-start-reverse"
              >
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--color-primary)" />
              </marker>
              <marker
                id="arrow-warning"
                viewBox="0 0 10 10"
                refX="9"
                refY="5"
                markerWidth="5"
                markerHeight="5"
                orient="auto"
              >
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--color-warning)" />
              </marker>
            </defs>
            <rect width="100%" height="100%" fill="url(#dots)" />
            {[
              "SOURCE LOT",
              "MIX / RELATED LOT",
              "FINISHED BATCH",
              "REPACK / REWORK",
            ].map((s, i) => (
              <text
                key={s}
                x={30 + i * 205}
                y="24"
                className="graph-column-label"
              >
                {s}
              </text>
            ))}
            {layout.edges.map((e) => {
              const a = layout.positions.get(e.source)!,
                b = layout.positions.get(e.target)!;
              const warning = e.evidence !== "confirmed";
              return (
                <g key={e.source + e.target}>
                  <path
                    d={`M${a.x + 160},${a.y + 33} C${a.x + 190},${a.y + 33} ${b.x - 32},${b.y + 33} ${b.x - 5},${b.y + 33}`}
                    fill="none"
                    stroke={
                      warning ? "var(--color-warning)" : "var(--color-primary)"
                    }
                    strokeWidth={active.has(e.target) ? 2.2 : 1.5}
                    strokeDasharray={warning ? "5 5" : undefined}
                    opacity={
                      result && !active.has(e.target) && !warning ? 0.32 : 0.75
                    }
                    markerEnd={warning ? "url(#arrow-warning)" : "url(#arrow)"}
                  />
                </g>
              );
            })}
            {layout.nodes.map((n) => {
              const p = layout.positions.get(n.id)!;
              const warn = layout.edges.some(
                (e) => e.target === n.id && e.evidence !== "confirmed",
              );
              const isRoot = n.id === root;
              const shipments = graph.edges
                .filter((e) => e.source === n.id && e.kind === "DISPATCHED")
                .map((e) => graph.nodes.find((n) => n.id === e.target)!);
              const desc = shipments.length
                ? `${shipments.length} shipment${shipments.length > 1 ? "s" : ""} · ${number(shipments.reduce((s, n) => s + (n.units || 0), 0))} units`
                : isRoot
                  ? graph.edges.some(
                      (e) => e.kind === "ABOUT" && e.target === root,
                    )
                    ? "Supplier alert"
                    : "Investigation root"
                  : n.kind === "Rework"
                    ? "Hidden rework route"
                    : "Signed production record";
              return (
                <g
                  key={n.id}
                  role="button"
                  tabIndex={0}
                  aria-label={`Open ${n.id} evidence`}
                  onClick={() => onNode(n)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      onNode(n);
                    }
                  }}
                  className={`graph-node ${isRoot ? "root-node" : ""} ${warn ? "uncertain-node" : ""}`}
                >
                  <rect
                    x={p.x}
                    y={p.y}
                    width="160"
                    height="70"
                    rx="7"
                    fill="var(--color-surface)"
                    stroke={
                      isRoot
                        ? "var(--color-danger)"
                        : warn
                          ? "var(--color-warning)"
                          : "var(--color-line)"
                    }
                    strokeWidth={isRoot ? 1.6 : 1.2}
                  />
                  <rect
                    x={p.x}
                    y={p.y + 9}
                    width="3"
                    height="52"
                    rx="1.5"
                    fill={
                      isRoot
                        ? "var(--color-danger)"
                        : warn
                          ? "var(--color-warning)"
                          : "var(--color-primary)"
                    }
                  />
                  <text x={p.x + 13} y={p.y + 23} className="node-id">
                    {n.id}
                  </text>
                  <text x={p.x + 13} y={p.y + 43} className="node-name">
                    {n.name.split(" · ")[0]}
                  </text>
                  <text x={p.x + 13} y={p.y + 59} className="node-note">
                    {warn ? "Missing signed record" : desc}
                  </text>
                  {n.kind === "Rework" ? (
                    <circle
                      cx={p.x + 146}
                      cy={p.y + 16}
                      r="4"
                      fill="var(--color-accent)"
                    />
                  ) : null}
                </g>
              );
            })}
          </svg>
        </div>
      </div>
      <footer className="graph-footer">
        <div className="legend">
          <span>
            <i className="legend-line" />
            Confirmed record
          </span>
          <span>
            <i className="legend-line dashed" />
            Needs evidence
          </span>
        </div>
        <div className="zoom-controls">
          <button
            onClick={() => setZoom((v) => Math.max(0.75, v - 0.1))}
            aria-label="Zoom out"
          >
            <Minus size={14} />
          </button>
          <span>{Math.round(zoom * 100)}%</span>
          <button
            onClick={() => setZoom((v) => Math.min(1.4, v + 0.1))}
            aria-label="Zoom in"
          >
            <Plus size={14} />
          </button>
          <button onClick={() => setZoom(1)} aria-label="Reset graph zoom">
            <RotateCcw size={14} />
          </button>
        </div>
      </footer>
    </section>
  );
}
