import React from "react";
import {
  AbsoluteFill,
  Sequence,
  useCurrentFrame,
  interpolate,
  spring,
  useVideoConfig,
} from "remotion";

interface Section {
  title: string;
  content: string;
  durationInFrames: number;
}

interface ExplainerVideoProps {
  title: string;
  subtitle: string;
  sections: Section[];
}

const TitleCard: React.FC<{ title: string; subtitle: string }> = ({
  title,
  subtitle,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleScale = spring({ frame, fps, config: { damping: 12 } });
  const subtitleOpacity = interpolate(frame, [20, 40], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #0f0c29, #302b63, #24243e)",
        justifyContent: "center",
        alignItems: "center",
        flexDirection: "column",
      }}
    >
      <h1
        style={{
          fontSize: 80,
          fontWeight: "bold",
          color: "#ffffff",
          transform: `scale(${titleScale})`,
          textAlign: "center",
          margin: "0 40px",
        }}
      >
        {title}
      </h1>
      <p
        style={{
          fontSize: 36,
          color: "#a8a4ff",
          opacity: subtitleOpacity,
          marginTop: 20,
        }}
      >
        {subtitle}
      </p>
    </AbsoluteFill>
  );
};

const SectionCard: React.FC<{ title: string; content: string }> = ({
  title,
  content,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const slideIn = spring({ frame, fps, config: { damping: 15 } });
  const contentOpacity = interpolate(frame, [15, 30], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #1a1a2e, #16213e)",
        justifyContent: "center",
        alignItems: "center",
        padding: 80,
      }}
    >
      <div
        style={{
          transform: `translateX(${interpolate(slideIn, [0, 1], [-100, 0])}px)`,
          maxWidth: 1400,
        }}
      >
        <h2
          style={{
            fontSize: 56,
            color: "#00d4ff",
            marginBottom: 30,
            fontWeight: "bold",
          }}
        >
          {title}
        </h2>
        <p
          style={{
            fontSize: 32,
            color: "#e0e0e0",
            lineHeight: 1.6,
            opacity: contentOpacity,
          }}
        >
          {content}
        </p>
      </div>
    </AbsoluteFill>
  );
};

export const ExplainerVideo: React.FC<ExplainerVideoProps> = ({
  title,
  subtitle,
  sections,
}) => {
  const titleDuration = 90; // 3 seconds at 30fps

  return (
    <AbsoluteFill>
      <Sequence durationInFrames={titleDuration}>
        <TitleCard title={title} subtitle={subtitle} />
      </Sequence>
      {sections.map((section, index) => {
        const startFrame =
          titleDuration +
          sections
            .slice(0, index)
            .reduce((sum, s) => sum + s.durationInFrames, 0);
        return (
          <Sequence
            key={index}
            from={startFrame}
            durationInFrames={section.durationInFrames}
          >
            <SectionCard title={section.title} content={section.content} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
