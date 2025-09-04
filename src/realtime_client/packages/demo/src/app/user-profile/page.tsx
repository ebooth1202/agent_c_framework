/**
 * User Profile Page
 * Demonstrates accessing and displaying full user data from auth context
 */

import dynamicImport from 'next/dynamic';
import { Skeleton } from '@/components/ui/skeleton';

// Force dynamic rendering to prevent static generation issues
export const dynamic = 'force-dynamic';
export const revalidate = 0;

// Dynamically import the client component with no SSR
const UserProfileClient = dynamicImport(
  () => import('./UserProfileClient'),
  { 
    ssr: false,
    loading: () => (
      <div className="container mx-auto py-8">
        <div className="max-w-4xl mx-auto space-y-6">
          <div className="space-y-2">
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-4 w-full" />
          </div>
          <div className="space-y-4">
            <Skeleton className="h-64 w-full" />
          </div>
        </div>
      </div>
    )
  }
);

export default function UserProfilePage() {
  return <UserProfileClient />;
}