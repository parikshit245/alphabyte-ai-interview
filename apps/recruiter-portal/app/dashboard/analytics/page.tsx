import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@repo/ui";

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
        <p className="text-muted-foreground">Insights into your hiring pipeline.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Candidates by Stage</CardTitle>
            <CardDescription>Distribution of candidates across hiring stages</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] flex items-center justify-center bg-muted/20 border-dashed rounded-md">
              <span className="text-muted-foreground">Donut Chart Placeholder</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Time to Hire</CardTitle>
            <CardDescription>Average days to hire by role</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] flex items-center justify-center bg-muted/20 border-dashed rounded-md">
              <span className="text-muted-foreground">Bar Chart Placeholder</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
