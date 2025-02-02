import React from 'react'
import { Badge } from './ui/badge'
import Image from 'next/image'
import GmailIcon from "@/public/icons/gmail.png";
import GoogleCalendarIcon from "@/public/icons/google-calendar.png";
import { cn } from '@/lib/utils';

export default function IconBadge({
  icon,
  className
}: {
  icon: "gmail" | "google-calendar",
  className: string | undefined | null
}) {
  return (
    <Badge variant="secondary" className={cn("flex flex-row gap-1.5 items-center justify-self-start", className)}>
      {
        icon === 'gmail' && (
          <>
            <Image src={GmailIcon} alt="Gmail" width={12} height={12} />
            Gmail
          </>
        )
      }
      {
        icon === 'google-calendar' && (
          <>
            <Image src={GoogleCalendarIcon} alt="Google Calendar" width={12} height={12} />
            Google Calendar
          </>
        )
      }
    </Badge>
  )
}
