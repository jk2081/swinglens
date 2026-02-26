import { LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Skeleton } from '@/components/ui/skeleton';
import { useCoachQueue } from '@/hooks/use-coach-queue';
import { useAuthStore } from '@/stores/auth-store';
import type { ReviewQueueItem } from '@/api/types';
import { cn } from '@/lib/utils';

function timeAgo(dateStr: string): string {
  const seconds = Math.floor((Date.now() - new Date(dateStr).getTime()) / 1000);
  if (seconds < 60) return 'just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

function playerInitials(name: string): string {
  return name
    .split(' ')
    .map((w) => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

function scoreBadgeVariant(score: number | null) {
  if (score === null) return 'secondary' as const;
  if (score >= 80) return 'default' as const;
  if (score >= 60) return 'secondary' as const;
  return 'destructive' as const;
}

function QueueItem({ item }: { item: ReviewQueueItem }) {
  return (
    <button className="flex w-full items-start gap-3 rounded-lg p-3 text-left transition-colors hover:bg-accent">
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary/20 text-xs font-semibold text-primary">
        {playerInitials(item.player.name)}
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-center justify-between gap-2">
          <span className="truncate text-sm font-medium">{item.player.name}</span>
          {item.overall_score !== null && (
            <Badge variant={scoreBadgeVariant(item.overall_score)} className="shrink-0 text-xs">
              {item.overall_score}
            </Badge>
          )}
        </div>
        <div className="mt-0.5 flex items-center gap-2 text-xs text-muted-foreground">
          {item.player.handicap !== null && <span>HC {item.player.handicap}</span>}
          {item.club_type && (
            <>
              <span>&middot;</span>
              <span className="capitalize">{item.club_type.replace('_', ' ')}</span>
            </>
          )}
        </div>
        {item.flagged_issue && (
          <p className="mt-1 truncate text-xs text-destructive">{item.flagged_issue}</p>
        )}
        <p className="mt-1 text-xs text-muted-foreground">{timeAgo(item.uploaded_at)}</p>
      </div>
    </button>
  );
}

function QueueSkeleton() {
  return (
    <div className="space-y-3 p-3">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="flex items-start gap-3">
          <Skeleton className="h-9 w-9 rounded-full" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-3 w-1/2" />
          </div>
        </div>
      ))}
    </div>
  );
}

export function Sidebar({ className }: { className?: string }) {
  const navigate = useNavigate();
  const logout = useAuthStore((s) => s.logout);
  const { data: queue, isLoading, isError } = useCoachQueue();

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  return (
    <aside
      className={cn(
        'flex h-screen w-72 flex-col border-r border-border bg-sidebar text-sidebar-foreground',
        className,
      )}
    >
      <div className="flex items-center justify-between px-4 py-4">
        <h1 className="text-lg font-bold text-primary">SwingLens</h1>
        <Button variant="ghost" size="icon" onClick={handleLogout} title="Sign out">
          <LogOut className="h-4 w-4" />
        </Button>
      </div>

      <Separator />

      <div className="px-4 py-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Review Queue
        </h2>
      </div>

      <ScrollArea className="flex-1">
        {isLoading && <QueueSkeleton />}
        {isError && (
          <p className="px-4 py-8 text-center text-sm text-muted-foreground">
            Failed to load queue.
          </p>
        )}
        {queue && queue.length === 0 && (
          <p className="px-4 py-8 text-center text-sm text-muted-foreground">No pending reviews.</p>
        )}
        {queue && queue.length > 0 && (
          <div className="space-y-1 px-2">
            {queue.map((item) => (
              <QueueItem key={item.id} item={item} />
            ))}
          </div>
        )}
      </ScrollArea>

      <Separator />
      <div className="px-4 py-3 text-xs text-muted-foreground">
        {queue ? `${queue.length} pending` : '...'}
      </div>
    </aside>
  );
}
