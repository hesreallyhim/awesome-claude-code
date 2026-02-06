import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  interpolate,
  spring,
  useVideoConfig,
} from "remotion";

interface SectionCardProps {
  title: string;
  content: string;
  index: number;
  accentColor?: string;
}

const icons: Record<string, string> = {
  Research: "🔍",
  Code: "💻",
  Publish: "🚀",
  Promote: "📢",
  Video: "🎬",
  Default: "▸",
};

export const SectionCard: React.FC<SectionCardProps> = ({
  title,
  content,
  index,
  accentColor = "#6366f1",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const slideX = spring({ frame, fps, config: { damping: 15 } });
  const contentOpacity = interpolate(frame, [15, 35], [0, 1], {
    extrapolateRight: "clamp",
  });
  const numberScale = spring({ frame: frame - 5, fps, config: { damping: 10 } });

  const icon = icons[title] || icons.Default;

  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(135deg, #0f0f1a 0%, ${accentColor}08 100%)`,
        justifyContent: "center",
        padding: "0 120px",
      }}
    >
      {/* Step number */}
      <div
        style={{
          position: "absolute",
          top: 60,
          right: 80,
          fontSize: 200,
          fontWeight: 900,
          color: `${accentColor}10`,
          transform: `scale(${Math.max(0, numberScale)})`,
        }}
      >
        {String(index + 1).padStart(2, "0")}
      </div>

      <div
        style={{
          transform: `translateX(${interpolate(slideX, [0, 1], [-80, 0])}px)`,
          maxWidth: 1200,
        }}
      >
        {/* Section title */}
        <div style={{ display: "flex", alignItems: "center", gap: 20, marginBottom: 30 }}>
          <span style={{ fontSize: 48 }}>{icon}</span>
          <h2
            style={{
              fontSize: 56,
              color: accentColor,
              fontWeight: 700,
              margin: 0,
            }}
          >
            {title}
          </h2>
        </div>

        {/* Left accent bar */}
        <div style={{ display: "flex", gap: 24 }}>
          <div
            style={{
              width: 4,
              backgroundColor: accentColor,
              borderRadius: 2,
              flexShrink: 0,
            }}
          />
          <p
            style={{
              fontSize: 34,
              color: "#d0d0e0",
              lineHeight: 1.7,
              opacity: contentOpacity,
              margin: 0,
            }}
          >
            {content}
          </p>
        </div>
      </div>
    </AbsoluteFill>
  );
};
