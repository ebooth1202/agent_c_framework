import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Agent_C',
  description: 'Real-time chat with AI agents',
  icons: {
    icon: '/favicon.png',
  },
};

export default function ChatLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
