import { useQuery } from '@tanstack/react-query';
import { api } from '@/api/client';
import type { ReviewQueueItem } from '@/api/types';

export function useCoachQueue() {
  return useQuery({
    queryKey: ['coach', 'queue'],
    queryFn: () => api.get<ReviewQueueItem[]>('/api/v1/coach/queue').then((r) => r.data),
    staleTime: 30 * 1000,
  });
}
