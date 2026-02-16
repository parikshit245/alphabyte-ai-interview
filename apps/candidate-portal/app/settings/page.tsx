import { Card, CardContent, CardDescription, CardHeader, CardTitle, Input, Button } from "@repo/ui";

export default function SettingsPage() {
  return (
    <div className="container mx-auto p-8 max-w-2xl">
      <h1 className="text-3xl font-bold mb-8">Settings</h1>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Profile</CardTitle>
          <CardDescription>Manage your profile information</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">First Name</label>
            <Input placeholder="John" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Last Name</label>
            <Input placeholder="Doe" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Email</label>
            <Input type="email" placeholder="john@example.com" />
          </div>
          <Button>Save Changes</Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Preferences</CardTitle>
          <CardDescription>Customize your experience</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-500">Preference settings coming soon</p>
        </CardContent>
      </Card>
    </div>
  );
}
