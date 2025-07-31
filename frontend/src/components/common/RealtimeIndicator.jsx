import React from 'react';
import { Badge } from ../ui/badge';
import { Button } from ../ui/button';
import { Wifi, WifiOff, RefreshCw, Clock } from 'lucide-react';
import { useRealtime } from '../../contexts/RealtimeContext';

const RealtimeIndicator = () => {
  const { isConnected, lastUpdate, forceSync } = useRealtime();

  const formatLastUpdate = (date) => {
    const now = new Date();
    const diff = Math.floor((now - date) / 1000);

    if (diff < 60) {
      return 'Agora mesmo';
    } else if (diff < 3600) {
      const minutes = Math.floor(diff / 60);
      return `${minutes}min atrás`;
    } else {
      const hours = Math.floor(diff / 3600);
      return `${hours}h atrás`;
    }
  };

  return (
    <div className="flex items-center space-x-2">
      <Badge 
        variant={isConnected ? "default" : "destructive"}
        className="flex items-center space-x-1"
      >
        {isConnected ? (
          <Wifi className="w-3 h-3" />
        ) : (
          <WifiOff className="w-3 h-3" />
        )}
        <span>{isConnected ? 'Online' : 'Offline'}</span>
      </Badge>

      <div className="flex items-center space-x-1 text-xs text-gray-500">
        <Clock className="w-3 h-3" />
        <span>{formatLastUpdate(lastUpdate)}</span>
      </div>

      <Button
        variant="ghost"
        size="sm"
        onClick={forceSync}
        className="h-6 w-6 p-0"
        title="Sincronizar dados"
      >
        <RefreshCw className="w-3 h-3" />
      </Button>
    </div>
  );
};

export default RealtimeIndicator;

