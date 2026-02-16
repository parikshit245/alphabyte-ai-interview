import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@repo/ui";

export default function CandidatesPage() {
  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">Candidates</h1>

      <Card>
        <CardHeader>
          <CardTitle>Candidate Pipeline</CardTitle>
          <CardDescription>Manage your candidates and their interview status</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-gray-500">No candidates in the pipeline</p>
        </CardContent>
      </Card>
    </div>
  );
}
