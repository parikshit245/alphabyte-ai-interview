import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@repo/ui";

export default function InterviewsPage() {
  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">My Interviews</h1>

      <Card>
        <CardHeader>
          <CardTitle>Interview Sessions</CardTitle>
          <CardDescription>All your past and upcoming interviews</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-gray-500">No interviews scheduled yet</p>
        </CardContent>
      </Card>
    </div>
  );
}
