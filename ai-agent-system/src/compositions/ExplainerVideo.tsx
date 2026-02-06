import React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import { Title } from "../components/Title";
import { SectionCard } from "../components/SectionCard";
import { Transition } from "../components/Transition";

export interface Section {
  title: string;
  content: string;
  durationInFrames: number;
}

interface ExplainerVideoProps {
  title: string;
  subtitle: string;
  sections: Section[];
  accentColor: string;
}

export const ExplainerVideo: React.FC<ExplainerVideoProps> = ({
  title,
  subtitle,
  sections,
  accentColor,
}) => {
  const titleDuration = 90;
  const transitionDuration = 15;

  let currentFrame = 0;

  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0a0f" }}>
      {/* Title Card */}
      <Sequence from={currentFrame} durationInFrames={titleDuration}>
        <Title text={title} subtitle={subtitle} accentColor={accentColor} />
      </Sequence>
      {(() => { currentFrame += titleDuration; return null; })()}

      {/* Content Sections */}
      {sections.map((section, index) => {
        const sectionStart = titleDuration + sections
          .slice(0, index)
          .reduce((sum, s) => sum + s.durationInFrames + transitionDuration, 0);

        return (
          <React.Fragment key={index}>
            <Sequence from={sectionStart} durationInFrames={transitionDuration}>
              <Transition direction={index % 2 === 0 ? "left" : "right"} />
            </Sequence>
            <Sequence
              from={sectionStart + transitionDuration}
              durationInFrames={section.durationInFrames}
            >
              <SectionCard
                title={section.title}
                content={section.content}
                index={index}
                accentColor={accentColor}
              />
            </Sequence>
          </React.Fragment>
        );
      })}
    </AbsoluteFill>
  );
};
