import React from 'react'
import { Card, CardHeader, CardTitle } from './ui/card'
import Image from 'next/image'
import GmailIcon from "@/public/icons/gmail.png";
import GoogleCalendarIcon from "@/public/icons/google-calendar.png";
import type { Action } from '@/types/actions';
import IconBadge from './IconBadge';

export default function Action({
  title,
  actions
}: {
  title: string;
  actions: Action[];
}) {
  return (
    <Card className='z-10 w-fit rounded-2xl bg-zinc-800 border-zinc-300 text-white relative'>
      <CardHeader className="flex flex-row items-center gap-8 space-y-0 p-0">
        <CardTitle className='mt-0 pt-0 text-2xl font-medium p-6'>{title}</CardTitle>
      </CardHeader>
      <div className='absolute -top-2 -right-2 flex gap-2'>
        <IconBadge icon='gmail' className='' />
        <IconBadge icon='google-calendar' className='' />
      </div>
    </Card>
  )
}
