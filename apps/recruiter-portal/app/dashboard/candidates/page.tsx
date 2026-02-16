import { Button, Card, CardContent, Table, TableHeader, TableRow, TableHead, TableBody, TableCell, Badge, Input } from "@repo/ui";
import { Search, Filter, MoreHorizontal } from "lucide-react";

export default function CandidatesPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Candidates</h1>
          <p className="text-muted-foreground">View and manage candidate applications.</p>
        </div>
      </div>

      <div className="flex items-center gap-4">
         <div className="relative flex-1">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input type="search" placeholder="Search candidates..." className="pl-9 w-[300px]" />
         </div>
         <Button variant="outline"><Filter className="mr-2 h-4 w-4" /> Filter</Button>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Applied For</TableHead>
                <TableHead>Date Applied</TableHead>
                <TableHead>Stage</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-medium">Alice Johnson</TableCell>
                <TableCell>Senior Frontend Engineer</TableCell>
                <TableCell>Oct 28, 2024</TableCell>
                <TableCell>
                  <Badge>Screening</Badge>
                </TableCell>
                <TableCell className="text-right">
                  <Button variant="ghost" size="icon">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Bob Smith</TableCell>
                <TableCell>Product Designer</TableCell>
                <TableCell>Oct 27, 2024</TableCell>
                <TableCell>
                  <Badge variant="outline" className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100 dark:bg-yellow-900 dark:text-yellow-300">Interview</Badge>
                </TableCell>
                <TableCell className="text-right">
                  <Button variant="ghost" size="icon">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
