import React from "react";
import { Composition } from "remotion";
import { ExplainerVideo } from "./compositions/ExplainerVideo";
import { DemoVideo } from "./compositions/DemoVideo";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="ExplainerVideo"
        component={ExplainerVideo}
        durationInFrames={30 * 60}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          title: "AI Agent Demo",
          subtitle: "Built with Claude Code",
          sections: [],
        }}
      />
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
    </>
  );
};
