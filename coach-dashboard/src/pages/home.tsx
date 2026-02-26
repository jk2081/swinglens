import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export function HomePage() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-center text-2xl text-primary">SwingLens</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-center text-muted-foreground">Coach Dashboard</p>
        </CardContent>
      </Card>
    </div>
  );
}
