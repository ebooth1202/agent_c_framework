// src/components/replay_interface/InteractionsPage.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_URL } from '@/config/config';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { formatDistanceToNow } from 'date-fns';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';
import { Trash2, Play } from 'lucide-react';

const InteractionsPage = () => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      // Using the correct API format
      const response = await fetch(`${API_URL}/interactions/`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setSessions(data);
    } catch (err) {
      console.error('Error fetching sessions:', err);
      setError('Failed to load sessions');
    } finally {
      setLoading(false);
    }
  };

  const handleSessionSelect = (sessionId) => {
    // This navigates to the enhanced version by default
    navigate(`/replay/${sessionId}`);
  };
  
  const handleDeleteSession = async (sessionId) => {
    try {
      const response = await fetch(`${API_URL}/interactions/${sessionId}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // Refresh the sessions list
      fetchSessions();
    } catch (err) {
      console.error('Error deleting session:', err);
      setError(`Failed to delete session ${sessionId}`);
    }
  };

  if (loading) return (
    <div className="flex items-center justify-center h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
    </div>
  );

  if (error) return (
    <div className="container mx-auto p-4">
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        <p>{error}</p>
      </div>
    </div>
  );

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Recorded Sessions</h1>

      {sessions.length === 0 ? (
        <div className="text-center p-8">No recorded sessions found.</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sessions.map((session) => (
            <Card key={session.id} className="p-4 hover:shadow-md transition-shadow">
              <div className="font-medium mb-2">Session ID: {session.id}</div>
              <div className="text-sm text-gray-500 mb-1">
                Started: {new Date(session.start_time).toLocaleString()}
              </div>
              <div className="text-sm text-gray-500 mb-1">
                Duration: {session.duration_seconds ? `${Math.round(session.duration_seconds)}s` : 'N/A'}
              </div>
              <div className="text-sm text-gray-500 mb-2">
                {session.event_count} events · {session.file_count} files
              </div>
              <div className="flex space-x-2">
                <Button
                  onClick={() => handleSessionSelect(session.id)}
                  className="flex-1 flex items-center justify-center"
                  variant="default"
                >
                  <Play className="mr-2 h-4 w-4" />
                  View Replay
                </Button>
                
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button variant="destructive">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Delete Session</AlertDialogTitle>
                      <AlertDialogDescription>
                        Are you sure you want to delete this session? This action cannot be undone.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction onClick={() => handleDeleteSession(session.id)}>
                        Delete
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default InteractionsPage;