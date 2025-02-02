"use client";

import Image from "next/image";
import Link from "next/link";
import { motion, useMotionValueEvent, useScroll } from "motion/react";
import Action from "@/components/Action";
import { useEffect, useRef, useState } from "react";

/* 
  1. On initial load, user will login to their Google account
  2. This page will then await gmail notifications. When received, the main API route will be called
    with the email data as a parameter.
  3. The API route will then process the email data and return up to 3 task suggestions.

*/

const exampleActions = [
  {
    title: "Mexico trip in June",
    actions: [
      {
        action: "Invite Fred",
        link: "mailto:fredthegamer20@mail.com",
      },
      {
        action: "Find flights",
        link: "https://flights.google.com",
      },
      {
        action: "Shop for bathing suits",
        link: "https://www.amazon.com/s?k=bathing+suits",
      },
    ],
  },
  {
    title: "Follow up with Sarah",
    actions: [
      {
        action: "Send an email to Sarah",
        link: "mailto:sarahwitch21@email.com",
      },
    ],
  },
  {
    title: "Dinner with friends on Friday",
    actions: [
      {
        action: "Send an email to friends",
        link: "mailto:amythegreat@mail.com",
      },
      {
        action: "Create a calendar event",
        link: "https://calendar.google.com",
      },
    ],
  },
  {
    title: "Gift ideas for mom's birthday",
    actions: [
      {
        action: "Apron from Amazon",
        link: "https://www.amazon.com/s?k=apron",
      },
      {
        action: "Book from Indigo",
        link: "https://www.chapters.indigo.ca/en-ca/books/",
      },
    ],
  },
];

export default function Home() {
  const userName = "Adamo";

  const containerRef = useRef(null);
  const { scrollY } = useScroll({
    container: containerRef, // Tracks scroll position of the container
  });

  const [currentActionIndex, setCurrentActionIndex] = useState(0);

  useMotionValueEvent(scrollY, "change", (current) => {
    // Get y coordinate of each action card
    const actionYs = exampleActions.map((_, i) => {
      const action = document.getElementById(`action-${i}`);
      return action?.getBoundingClientRect().y;
    });

    // Find the index of the action card that is closest to the middle of the viewport
    const viewportMiddle = window.innerHeight / 2;

    const diffs = actionYs.map(y => Math.abs((y ?? 0) - viewportMiddle));
    const minDiff = Math.min(...diffs);
    const closestIndex = diffs.findIndex((diff) => diff === minDiff);

    setCurrentActionIndex(closestIndex);
  });

  return (
    <main className="flex h-screen flex-col items-center px-24 py-12 bg-gradient-to-b from-zinc-900 bg-zinc-950 text-white">
      <div className="flex flex-col items-center w-full h-full">
        {/* {exampleActions.filter((_, i) => i < currentActionIndex).length ===
          0 && <div>Good morning, {userName}.</div>} */}
        <div
          ref={containerRef}
          className="w-full overflow-y-auto overflow-x-hidden flex flex-col items-center h-full gap-20 py-80 px-6 snap-y snap-mandatory scroll-smooth"
        >
            {
              exampleActions.map((action, index) => (
                <motion.div
                  id={`action-${index}`}
                  key={index}
                  animate={{
                    opacity: 1 - Math.abs(index - currentActionIndex) / exampleActions.length,
                    scale:
                      1 - Math.abs(index - currentActionIndex) / exampleActions.length,
                    filter: index !== currentActionIndex ? "blur(7.5px)" : "blur(0)",
                  }}
                  className="snap-center snap-always"
                >
                  <Action title={action.title} actions={action.actions} />
                </motion.div>
              ))
            }
        </div>
      </div>
    </main>
  );
}
