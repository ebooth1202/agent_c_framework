// src/components/replay_interface/EventDisplay.jsx
import React, {useState} from 'react';
import {Card} from '@/components/ui/card';
import {Badge} from '@/components/ui/badge';
import {Collapsible, CollapsibleContent, CollapsibleTrigger} from '@/components/ui/collapsible';
import {ChevronRight, ChevronDown} from 'lucide-react';

const EventDisplay = ({event}) => {
    const [isOpen, setIsOpen] = useState(false);

    // Safely get event type and role
    const getEventType = () => {
        if (event.raw?.event?.type) return event.raw.event.type;
        if (event.event?.type) return event.event.type;
        if (event.type) return event.type;
        return "unknown";
    };

    const getEventRole = () => {
        if (event.raw?.event?.role) return event.raw.event.role;
        if (event.event?.role) return event.event.role;
        if (event.role) return event.role;
        return null;
    };

    return (
        <Card className="p-3">
            <Collapsible
                open={isOpen}
                onOpenChange={setIsOpen}
                className="w-full"
            >
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        <CollapsibleTrigger className="flex items-center">
                            {isOpen ? (
                                <ChevronDown className="h-4 w-4 text-gray-500"/>
                            ) : (
                                <ChevronRight className="h-4 w-4 text-gray-500"/>
                            )}
                        </CollapsibleTrigger>
                        <Badge>{getEventType()}</Badge>
                        {getEventRole() && (
                            <Badge variant="outline">{getEventRole()}</Badge>
                        )}
                    </div>
                    <span className="text-xs text-gray-500">
            {new Date(event.timestamp || Date.now()).toLocaleTimeString()}
          </span>
                </div>

                <CollapsibleContent className="mt-2">
          <pre className="bg-gray-50 p-2 rounded text-xs overflow-auto max-h-96">
            {JSON.stringify(event, null, 2)}
          </pre>
                </CollapsibleContent>
            </Collapsible>
        </Card>
    );
};

export default EventDisplay;