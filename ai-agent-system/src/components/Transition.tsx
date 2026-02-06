import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";

interface TransitionProps {
  direction?: "left" | "right" | "up" | "down";
  color?: string;
}

export const Transition: React.FC<TransitionProps> = ({
  direction = "left",
  color = "#6366f1",
}) => {
  const frame = useCurrentFrame();

  const progress = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: "clamp",
  });

  const transforms: Record<string, string> = {
    left: `translateX(${interpolate(progress, [0, 0.5, 1], [-100, 0, 100])}%)`,
    right: `translateX(${interpolate(progress, [0, 0.5, 1], [100, 0, -100])}%)`,
    up: `translateY(${interpolate(progress, [0, 0.5, 1], [-100, 0, 100])}%)`,
    down: `translateY(${interpolate(progress, [0, 0.5, 1], [100, 0, -100])}%)`,
  };

  return (
    <AbsoluteFill
      style={{
        backgroundColor: color,
        opacity: interpolate(progress, [0, 0.3, 0.7, 1], [0, 0.6, 0.6, 0]),
        transform: transforms[direction],
      }}
    />
  );
};
