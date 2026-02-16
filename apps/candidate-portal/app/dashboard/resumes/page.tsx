"use client";

import { useEffect, useState } from "react";
import {
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Table,
  TableHeader,
  TableRow,
  TableHead,
  TableBody,
  TableCell,
  Input,
  Label,
} from "@repo/ui";
import { Upload, FileText, Trash2 } from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

type Resume = {
  id: string;
  fileName: string;
  fileUrl: string;
  createdAt: string;
};

export default function ResumesPage() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [webProfileUrl, setWebProfileUrl] = useState(""); // Stub for website profile
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const { user } = useAuth();

  useEffect(() => {
    if (user?.id) fetchResumes();
  }, [user]);

  const fetchResumes = async () => {
    if (!user?.id) return;
    try {
      const data = await api.get<Resume[]>(`/resumes?userId=${user.id}`);
      setResumes(data);
    } catch (e) {
      console.error("Failed to fetch resumes", e);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    if (!user?.id) {
      alert("Please login first");
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("userId", user.id);

    try {
      await api.postMultipart("/resumes", formData);
      await fetchResumes();
      setSelectedFile(null);
    } catch (err) {
      console.error("Upload failed", err);
      alert("Failed to upload resume.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Profile & Resumes</h1>
        <p className="text-muted-foreground">Manage your profiles and uploaded resumes.</p>
      </div>

      {/* Website Profile Section */}
      <Card>
        <CardHeader>
          <CardTitle>Website Profile</CardTitle>
          <CardDescription>Link your personal portfolio or website.</CardDescription>
        </CardHeader>
        <CardContent className="flex gap-4">
          <div className="grid w-full max-w-sm items-center gap-1.5">
            <Label htmlFor="website">Website URL</Label>
            <Input
              type="url"
              id="website"
              placeholder="https://your-portfolio.com"
              value={webProfileUrl}
              onChange={(e) => setWebProfileUrl(e.target.value)}
            />
          </div>
          <div className="flex items-end">
            <Button variant="outline">Save</Button>
          </div>
        </CardContent>
      </Card>

      {/* Resume Section */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Resumes</CardTitle>
            <CardDescription>Upload tailored resumes for different roles.</CardDescription>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-end gap-4 border p-4 rounded-md bg-slate-50 dark:bg-slate-900">
            <div className="grid w-full max-w-sm items-center gap-1.5">
              <Label htmlFor="resume">Upload New Resume (PDF)</Label>
              <Input
                id="resume"
                type="file"
                accept=".pdf"
                onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
              />
            </div>
            <Button onClick={handleUpload} disabled={!selectedFile || uploading}>
              {uploading ? (
                "Uploading..."
              ) : (
                <>
                  <Upload className="mr-2 h-4 w-4" /> Upload
                </>
              )}
            </Button>
          </div>

          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>File Name</TableHead>
                  <TableHead>Date Uploaded</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {resumes.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={3} className="text-center h-24 text-muted-foreground">
                      No resumes uploaded yet.
                    </TableCell>
                  </TableRow>
                ) : (
                  resumes.map((resume) => (
                    <TableRow key={resume.id}>
                      <TableCell className="font-medium flex items-center gap-2">
                        <FileText className="h-4 w-4 text-blue-500" />
                        {resume.fileName}
                      </TableCell>
                      <TableCell>{new Date(resume.createdAt).toLocaleDateString()}</TableCell>
                      <TableCell className="text-right">
                        <Button variant="ghost" size="icon" className="text-red-500">
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
