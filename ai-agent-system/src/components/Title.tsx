import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  interpolate,
  spring,
  useVideoConfig,
} from "remotion";

interface TitleProps {
  text: string;
  subtitle?: string;
  accentColor?: string;
}

export const Title: React.FC<TitleProps> = ({
  text,
  subtitle,
  accentColor = "#6366f1",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleScale = spring({ frame, fps, config: { damping: 12, mass: 0.6 } });
  const subtitleOpacity = interpolate(frame, [25, 45], [0, 1], {
    extrapolateRight: "clamp",
  });
  const lineWidth = interpolate(frame, [10, 40], [0, 200], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse at center, ${accentColor}12 0%, #0a0a0f 70%)`,
        justifyContent: "center",
        alignItems: "center",
        flexDirection: "column",
      }}
    >
      <h1
        style={{
          fontSize: 84,
          fontWeight: 800,
          color: "#ffffff",
          transform: `scale(${titleScale})`,
          textAlign: "center",
          margin: "0 60px",
          letterSpacing: -2,
        }}
      >
        {text}
      </h1>

      {/* Accent line */}
      <div
        style={{
          width: lineWidth,
          height: 4,
          backgroundColor: accentColor,
          borderRadius: 2,
          marginTop: 20,
          marginBottom: 20,
        }}
      />

      {subtitle && (
        <p
          style={{
            fontSize: 32,
            color: `${accentColor}cc`,
            opacity: subtitleOpacity,
            fontWeight: 400,
            letterSpacing: 1,
          }}
        >
          {subtitle}
        </p>
      )}
    </AbsoluteFill>
  );
};
