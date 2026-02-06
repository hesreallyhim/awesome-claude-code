import React from "react";
import { useCurrentFrame, interpolate } from "remotion";

interface CaptionProps {
  text: string;
  position?: "bottom" | "top";
}

export const Caption: React.FC<CaptionProps> = ({
  text,
  position = "bottom",
}) => {
  const frame = useCurrentFrame();

  const opacity = interpolate(frame, [0, 8, -1], [0, 1, 1], {
    extrapolateRight: "clamp",
  });
  const translateY = interpolate(frame, [0, 8], [20, 0], {
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "absolute",
        [position]: 80,
        left: 0,
        right: 0,
        textAlign: "center",
        zIndex: 100,
        opacity,
        transform: `translateY(${translateY}px)`,
      }}
    >
      <span
        style={{
          backgroundColor: "rgba(0, 0, 0, 0.82)",
          color: "#ffffff",
          fontSize: 34,
          padding: "14px 36px",
          borderRadius: 10,
          fontFamily: "system-ui, -apple-system, sans-serif",
          fontWeight: 500,
          letterSpacing: 0.3,
          boxShadow: "0 8px 32px rgba(0,0,0,0.3)",
        }}
      >
        {text}
      </span>
    </div>
  );
};
