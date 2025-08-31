"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import { LogOut, Mic } from "lucide-react"

import { isAuthenticated, logout, getCurrentUser } from "@/lib/auth"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export default function DashboardPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = React.useState(false)
  const [user, setUser] = React.useState<any>(null)

  // Check authentication on mount
  React.useEffect(() => {
    // Redirect to login if not authenticated
    if (!isAuthenticated()) {
      router.push("/login")
      return
    }

    // Get current user info
    const currentUser = getCurrentUser()
    setUser(currentUser)
  }, [router])

  // Handle logout
  const handleLogout = async () => {
    setIsLoading(true)
    try {
      await logout()
      router.push("/login")
    } catch (error) {
      console.error("Logout error:", error)
      // Even if logout fails, redirect to login
      router.push("/login")
    } finally {
      setIsLoading(false)
    }
  }

  // Don't render until auth check is complete
  if (!user) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-semibold">Agent C Dashboard</h1>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={handleLogout}
            disabled={isLoading}
            aria-label="Logout"
          >
            <LogOut className="mr-2 h-4 w-4" />
            {isLoading ? "Logging out..." : "Logout"}
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="grid gap-6">
          {/* Welcome Card */}
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl">
                Welcome back{user?.sub ? `, ${user.sub}` : ""}!
              </CardTitle>
              <CardDescription className="text-muted-foreground">
                You have successfully logged into the Agent C Realtime system.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Your authentication token is valid and you can now access the realtime features.
              </p>
            </CardContent>
          </Card>

          {/* Realtime Interface Placeholder */}
          <Card className="border-dashed">
            <CardHeader>
              <div className="flex items-center gap-2">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                  <Mic className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <CardTitle>Realtime Interface</CardTitle>
                  <CardDescription className="text-muted-foreground">
                    Coming Soon
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  The realtime voice and chat interface will be added here. This will include:
                </p>
                <ul className="list-inside list-disc space-y-1 text-sm text-muted-foreground">
                  <li>Voice-to-voice conversations with AI agents</li>
                  <li>Real-time text chat capabilities</li>
                  <li>Avatar streaming support</li>
                  <li>Multi-agent selection</li>
                  <li>Audio level visualization</li>
                  <li>Connection status monitoring</li>
                </ul>
                <div className="rounded-lg bg-muted/50 p-4">
                  <p className="text-xs text-muted-foreground">
                    <strong>Note:</strong> This dashboard confirms that authentication is working correctly. 
                    The full realtime interface components will be integrated once the SDK connection is established.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Status Card */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">System Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-2">
                <div className="flex items-center justify-between rounded-lg bg-green-500/10 px-3 py-2">
                  <span className="text-sm font-medium">Authentication</span>
                  <span className="text-sm text-green-600 dark:text-green-400">Active</span>
                </div>
                <div className="flex items-center justify-between rounded-lg bg-yellow-500/10 px-3 py-2">
                  <span className="text-sm font-medium">Realtime Connection</span>
                  <span className="text-sm text-yellow-600 dark:text-yellow-400">Not Connected</span>
                </div>
                <div className="flex items-center justify-between rounded-lg bg-muted px-3 py-2">
                  <span className="text-sm font-medium">Agent Status</span>
                  <span className="text-sm text-muted-foreground">Awaiting Connection</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}