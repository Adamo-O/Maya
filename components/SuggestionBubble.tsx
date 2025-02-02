import Link from "next/link";
import { motion } from "motion/react";
import { Action } from "@/types/actions";

export default function SuggestionBubble({
  action,
  position,
  totalBubbles,
}: {
  action: Action;
  position: number;
  totalBubbles: number;
}) {
  let x = "-50%";
  let y = -60;
  let top = "21%";
  let rotate = "0deg";
  if (totalBubbles === 2) {
    if (position === 1) {
      y = -100;
      top = "-24%";
      rotate = "-5deg";
    } else {
      y = -20;
      top = "44%";
      rotate = "5deg";
    }
  }
  if (totalBubbles === 3) {
    if (position === 1) {
      y = -120;
      top = "-24%";
      rotate = "-8deg";
    } else if (position === 2) {
      y = -60;
      top = "21%";
      rotate = "0deg";
    } else {
      y = 5;
      top = "44%";
      rotate = "8deg";
    }
  }

  return (
    <motion.div
      initial={{ z: -100, opacity: 0, x: "-100%", y: -60 }}
      animate={{ z: -100, opacity: 1, x, y, transition: { delay: 0.5 } }}
      whileHover={{
        scale: 1.025,
        transition: { bounce: 0.3, ease: "easeInOut" },
      }}
    >
      <Link href={action.link} target="_blank" rel="noopener noreferrer">
        <div
          className="bg-zinc-300/80 backdrop-blur-sm rounded-3xl px-3 py-2 border-zinc-800 border text-black text-start w-max"
          style={{
            position: "absolute",
            top: top,
            left: "165%",
            cursor: "pointer",
            rotate: rotate,
          }}
        >
          {action.action}
        </div>
      </Link>
    </motion.div>
  );
}
