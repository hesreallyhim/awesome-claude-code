import React from "react";
import {
  AbsoluteFill,
  Sequence,
  useCurrentFrame,
  interpolate,
  spring,
  useVideoConfig,
} from "remotion";

interface ShortVideoProps {
  lines: string[];
  accentColor: string;
}

const TextLine: React.FC<{ text: string; color: string }> = ({ text, color }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({ frame, fps, config: { damping: 12, mass: 0.8 } });
  const opacity = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        background: `linear-gradient(180deg, #0a0a0f 0%, ${color}15 100%)`,
      }}
    >
      <div
        style={{
          transform: `scale(${scale})`,
          opacity,
          fontSize: 72,
          fontWeight: 900,
          color: "#ffffff",
          textAlign: "center",
          padding: "0 60px",
          lineHeight: 1.2,
          textShadow: `0 4px 40px ${color}60`,
        }}
      >
        {text}
      </div>
    </AbsoluteFill>
  );
};

const FinalCard: React.FC<{ color: string }> = ({ color }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const scale = spring({ frame, fps, config: { damping: 15 } });

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        background: `linear-gradient(135deg, #0a0a0f, ${color}30)`,
      }}
    >
      <div
        style={{
          transform: `scale(${scale})`,
          textAlign: "center",
        }}
      >
        <div style={{ fontSize: 48, color: "#ffffff80", marginBottom: 20 }}>
          Follow for more
        </div>
        <div style={{ fontSize: 36, color }}>
          github.com/AllAboutAI-YT
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const ShortVideo: React.FC<ShortVideoProps> = ({ lines, accentColor }) => {
  const framesPerLine = 60; // 2 seconds per line

  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0a0f" }}>
      {lines.map((line, i) => (
        <Sequence
          key={i}
          from={i * framesPerLine}
          durationInFrames={framesPerLine}
        >
          <TextLine text={line} color={accentColor} />
        </Sequence>
      ))}

      {/* Final CTA card */}
      <Sequence
        from={lines.length * framesPerLine}
        durationInFrames={90}
      >
        <FinalCard color={accentColor} />
      </Sequence>
    </AbsoluteFill>
  );
};
