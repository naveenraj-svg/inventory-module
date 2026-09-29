const TONES = { LOW: "bad", NORMAL: "good", IN: "good", OUT: "neutral", Active: "good", Inactive: "muted" };
const LABELS = { LOW: "Low", NORMAL: "Normal", IN: "In", OUT: "Out" };

export default function Badge({ value }) {
  return <span className={`badge badge-${TONES[value] || "muted"}`}>{LABELS[value] || value}</span>;
}
