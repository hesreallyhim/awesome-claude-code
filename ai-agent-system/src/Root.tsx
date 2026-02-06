import React from "react";
import { Composition } from "remotion";
import { ExplainerVideo } from "./compositions/ExplainerVideo";
import { DemoVideo } from "./compositions/DemoVideo";
import { ShortVideo } from "./compositions/ShortVideo";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* Landscape explainer video — YouTube / blog embeds */}
      <Composition
        id="ExplainerVideo"
        component={ExplainerVideo}
        durationInFrames={30 * 60}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          title: "AI Agent System",
          subtitle: "Built with Claude Code — No OpenClaw",
          sections: [
            {
              title: "Research",
              content: "Scan X, GitHub, HN for trending topics and brainstorm project ideas.",
              durationInFrames: 150,
            },
            {
              title: "Code",
              content: "Build a complete project from scratch — React, Node.js, Python, anything.",
              durationInFrames: 150,
            },
            {
              title: "Publish",
              content: "Push to GitHub with proper commits, README, and release tags.",
              durationInFrames: 120,
            },
            {
              title: "Promote",
              content: "Post on X and LinkedIn with optimized content and native media.",
              durationInFrames: 120,
            },
          ],
          accentColor: "#6366f1",
        }}
      />

      {/* Landscape demo video — screenshots with captions */}
      <Composition
        id="DemoVideo"
        component={DemoVideo}
        durationInFrames={30 * 30}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          title: "Project Demo",
          screenshotPaths: [],
          captions: [],
        }}
      />

      {/* Vertical short for social media */}
      <Composition
        id="ShortVideo"
        component={ShortVideo}
        durationInFrames={30 * 20}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          lines: [
            "I built an AI agent",
            "that trains itself",
            "to post on X and LinkedIn",
            "create videos",
            "and publish to GitHub",
            "All with Claude Code",
            "No OpenClaw needed",
          ],
          accentColor: "#f97316",
        }}
      />
    </>
  );
};
